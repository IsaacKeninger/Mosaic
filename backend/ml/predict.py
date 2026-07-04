"""Load the trained K-Means/scaler/PCA artifacts from S3 to classify one user
at a time (used by the classify-user Lambda/route, as opposed to train.py's
batch retraining path)."""
import os
import tempfile

import boto3
import joblib
import numpy as np


def _download_and_load(s3, bucket: str, name: str, tmp_dir: str):
    path = os.path.join(tmp_dir, f"{name}.joblib")
    s3.download_file(bucket, f"{name}.joblib", path)
    return joblib.load(path)


def load_model_artifacts() -> tuple:
    """Returns (kmeans, scaler, pca). Raises if train.py hasn't been run yet."""
    bucket = os.environ["S3_MODEL_BUCKET"]
    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    with tempfile.TemporaryDirectory() as tmp_dir:
        kmeans = _download_and_load(s3, bucket, "kmeans", tmp_dir)
        scaler = _download_and_load(s3, bucket, "scaler", tmp_dir)
        pca = _download_and_load(s3, bucket, "pca", tmp_dir)
    return kmeans, scaler, pca


def classify_feature_vector(feature_vector: np.ndarray) -> tuple[int, tuple[float, float]]:
    """Scale + cluster + project a single user's raw feature vector using the
    artifacts train.py already fit on the full population."""
    kmeans, scaler, pca = load_model_artifacts()
    X = scaler.transform(feature_vector.reshape(1, -1))
    cluster_id = int(kmeans.predict(X)[0])
    x, y = pca.transform(X)[0]
    return cluster_id, (float(x), float(y))
