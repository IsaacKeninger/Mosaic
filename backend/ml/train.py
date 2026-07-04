"""Model training entrypoint: feature matrix -> clustered + serialized model.

Pipeline (see CLAUDE.md > ML Pipeline):
1. Load feature matrix from DynamoDB
2. Normalize with StandardScaler
3. Run elbow method (K=2 to 10) to find optimal K
4. Evaluate with silhouette score (target > 0.35)
5. Train final K-Means model with optimal K
6. Also train DBSCAN for comparison
7. Run PCA (2 components) for visualization coordinates
8. Serialize model with joblib, upload to S3
9. Store cluster centroids + PCA coordinates in DynamoDB
"""
import os
import tempfile
from decimal import Decimal

import boto3
import joblib
import numpy as np
import pandas as pd

from backend.db import list_user_ids, personas_table, users_table
from backend.features.constants import FEATURE_COLUMNS
from backend.features.engineer import engineer_features
from backend.ml.cluster import fit_dbscan, fit_kmeans, scale_features
from backend.ml.evaluate import evaluate_clustering
from backend.ml.pca import fit_pca
from backend.plaid.sync import load_transactions

MIN_K = 2
MAX_K = 10


def load_feature_matrix() -> pd.DataFrame:
    """Pull every known user's transactions from DynamoDB and engineer features."""
    user_ids = list_user_ids()
    rows = {user_id: engineer_features(load_transactions(user_id)) for user_id in user_ids}
    return pd.DataFrame.from_dict(rows, orient="index", columns=FEATURE_COLUMNS)


def choose_optimal_k(X: np.ndarray, k_range: range) -> tuple[int, dict[int, float]]:
    """Fit K-Means across k_range and return the k with the best silhouette score."""
    silhouette_by_k = {}
    for k in k_range:
        labels = fit_kmeans(X, k).labels_
        silhouette_by_k[k] = evaluate_clustering(X, labels)["silhouette_score"]
    best_k = max(silhouette_by_k, key=silhouette_by_k.get)
    return best_k, silhouette_by_k


def _persona_id_for_cluster(cluster_id: int) -> str:
    return f"persona-{cluster_id}"


def _upload_model_to_s3(kmeans, scaler, pca) -> None:
    bucket = os.environ["S3_MODEL_BUCKET"]
    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    with tempfile.TemporaryDirectory() as tmp_dir:
        artifacts = {"kmeans": kmeans, "scaler": scaler, "pca": pca}
        for name, obj in artifacts.items():
            path = os.path.join(tmp_dir, f"{name}.joblib")
            joblib.dump(obj, path)
            s3.upload_file(path, bucket, f"{name}.joblib")


def _store_results(feature_matrix: pd.DataFrame, labels: np.ndarray, pca_coords: np.ndarray) -> None:
    users = users_table()
    personas = personas_table()

    for (user_id, features), cluster_id, (x, y) in zip(feature_matrix.iterrows(), labels, pca_coords):
        users.update_item(
            Key={"userId": user_id},
            UpdateExpression="SET clusterId = :c, personaId = :p, featureVector = :f, pcaCoordinates = :pca",
            ExpressionAttributeValues={
                ":c": int(cluster_id),
                ":p": _persona_id_for_cluster(int(cluster_id)),
                ":f": {k: Decimal(str(v)) for k, v in features.items()},
                ":pca": {"x": Decimal(str(float(x))), "y": Decimal(str(float(y)))},
            },
        )

    feature_matrix = feature_matrix.assign(clusterId=labels)
    for cluster_id, group in feature_matrix.groupby("clusterId"):
        if cluster_id == -1:
            continue  # DBSCAN noise label; not applicable to K-Means output but guarded regardless
        centroid = group[FEATURE_COLUMNS].mean()
        personas.update_item(
            Key={"personaId": _persona_id_for_cluster(int(cluster_id))},
            UpdateExpression="SET clusterId = :c, centroidFeatures = :cf, memberCount = :mc",
            ExpressionAttributeValues={
                ":c": int(cluster_id),
                ":cf": {k: Decimal(str(v)) for k, v in centroid.items()},
                ":mc": len(group),
            },
        )


def train() -> None:
    feature_matrix = load_feature_matrix()
    n_samples = len(feature_matrix)
    if n_samples < MIN_K + 1:
        raise ValueError(
            f"Need at least {MIN_K + 1} users with synced transactions to cluster; found {n_samples}. "
            "Sync more Plaid Sandbox users first (see scripts/seed_dynamo.py)."
        )

    X, scaler = scale_features(feature_matrix.to_numpy())
    k_range = range(MIN_K, min(MAX_K, n_samples - 1) + 1)

    best_k, silhouette_by_k = choose_optimal_k(X, k_range)
    print(f"Silhouette by k: {silhouette_by_k}")
    print(f"Chosen k={best_k} (silhouette={silhouette_by_k[best_k]:.3f})")

    kmeans = fit_kmeans(X, best_k)
    kmeans_metrics = evaluate_clustering(X, kmeans.labels_)
    print(f"K-Means metrics: {kmeans_metrics}")

    dbscan = fit_dbscan(X)
    n_dbscan_clusters = len(set(dbscan.labels_) - {-1})
    if n_dbscan_clusters >= 2:
        dbscan_metrics = evaluate_clustering(X, dbscan.labels_)
        print(f"DBSCAN metrics ({n_dbscan_clusters} clusters, comparison only): {dbscan_metrics}")
    else:
        print("DBSCAN found fewer than 2 clusters on this dataset — skipping comparison metrics.")

    pca = fit_pca(X)
    pca_coords = pca.transform(X)

    _upload_model_to_s3(kmeans, scaler, pca)
    _store_results(feature_matrix, kmeans.labels_, pca_coords)

    print(f"Stored cluster assignments for {n_samples} users across {best_k} personas.")


if __name__ == "__main__":
    train()
