"""Generate persona descriptions from cluster centroids via Bedrock."""
import json
import os

from backend.bedrock.client import get_bedrock_client

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


def generate_persona(feature_summary: str, top_categories: str, behavioral_summary: str) -> dict:
    """Call Bedrock with a cluster centroid summary and parse the JSON persona.

    TODO: invoke_model against BEDROCK_MODEL_ID, parse the response body,
    and validate the returned JSON against the expected persona shape.
    """
    client = get_bedrock_client()
    prompt = PERSONA_PROMPT.format(
        feature_summary=feature_summary,
        top_categories=top_categories,
        behavioral_summary=behavioral_summary,
    )
    raise NotImplementedError
