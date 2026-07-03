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
from backend.ml.cluster import fit_dbscan, fit_kmeans, scale_features
from backend.ml.evaluate import elbow_method, evaluate_clustering
from backend.ml.pca import compute_pca_coordinates


def train() -> None:
    raise NotImplementedError("TODO: wire up steps 1-9 above")


if __name__ == "__main__":
    train()
