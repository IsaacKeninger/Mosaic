"""Generate persona descriptions from cluster centroids via Bedrock."""
import json
import os
import re

from backend.bedrock.client import get_bedrock_client
from backend.db import personas_table
from backend.features.constants import FEATURE_COLUMNS

PERSONA_PROMPT = """
You are a financial advisor analyzing a spending persona cluster.

Cluster characteristics (normalized feature values):
{feature_summary}

Top spending categories: {top_categories}
Behavioral signals: {behavioral_summary}

Generate a financial persona with the following JSON structure:
{{
  "name": "Creative 2-3 word persona name (e.g. 'The Conscious Saver')",
  "description": "2-3 sentence personality description of this spender type",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "recommendations": [
    "Specific actionable recommendation 1",
    "Specific actionable recommendation 2",
    "Specific actionable recommendation 3"
  ]
}}

Return ONLY valid JSON. No preamble or explanation.
"""

_PCT_FEATURES = [c for c in FEATURE_COLUMNS if c.startswith("pct_")]
_BEHAVIORAL_FEATURES = [c for c in FEATURE_COLUMNS if not c.startswith("pct_")]

REQUIRED_PERSONA_KEYS = {"name", "description", "strengths", "weaknesses", "recommendations"}


def _extract_json(text: str) -> dict:
    """Parse the model's JSON response, tolerating an accidental ```json fence."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON object found in Bedrock response: {text!r}")
    payload = json.loads(match.group(0))
    missing = REQUIRED_PERSONA_KEYS - payload.keys()
    if missing:
        raise ValueError(f"Bedrock persona response missing keys {missing}: {payload!r}")
    return payload


def generate_persona(feature_summary: str, top_categories: str, behavioral_summary: str) -> dict:
    """Call Bedrock with a cluster centroid summary and parse the JSON persona."""
    client = get_bedrock_client()
    prompt = PERSONA_PROMPT.format(
        feature_summary=feature_summary,
        top_categories=top_categories,
        behavioral_summary=behavioral_summary,
    )

    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    }

    response = client.invoke_model(
        modelId=os.environ["BEDROCK_MODEL_ID"],
        body=json.dumps(body),
    )
    response_body = json.loads(response["body"].read())
    text = response_body["content"][0]["text"]
    return _extract_json(text)


def _describe_centroid(centroid: dict[str, float]) -> tuple[str, str, str]:
    """Turn a cluster centroid dict into the three prompt-ready summary strings."""
    feature_summary = ", ".join(f"{k}={float(v):.3f}" for k, v in centroid.items())

    top_categories = ", ".join(
        f"{k.replace('pct_', '')} ({float(centroid[k]):.0%})"
        for k in sorted(_PCT_FEATURES, key=lambda k: -float(centroid.get(k, 0)))[:3]
    )

    behavioral_summary = ", ".join(
        f"{k}={float(centroid[k]):.3f}" for k in _BEHAVIORAL_FEATURES if k in centroid
    )

    return feature_summary, top_categories, behavioral_summary


def generate_and_store_persona(persona_id: str) -> dict:
    """Load a cluster's centroid from DynamoDB, generate its persona via Bedrock,
    and write the result back onto the same mosaic-personas item."""
    table = personas_table()
    item = table.get_item(Key={"personaId": persona_id}).get("Item")
    if item is None or "centroidFeatures" not in item:
        raise ValueError(f"No centroid found for {persona_id} — run ml/train.py first.")

    feature_summary, top_categories, behavioral_summary = _describe_centroid(item["centroidFeatures"])
    persona = generate_persona(feature_summary, top_categories, behavioral_summary)

    table.update_item(
        Key={"personaId": persona_id},
        UpdateExpression="SET #n = :name, description = :desc, strengths = :s, weaknesses = :w, recommendations = :r",
        ExpressionAttributeNames={"#n": "name"},
        ExpressionAttributeValues={
            ":name": persona["name"],
            ":desc": persona["description"],
            ":s": persona["strengths"],
            ":w": persona["weaknesses"],
            ":r": persona["recommendations"],
        },
    )
    return persona
