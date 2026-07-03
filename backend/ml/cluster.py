"""K-Means and DBSCAN clustering over the engineered feature matrix."""
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from sklearn.preprocessing import StandardScaler


def fit_kmeans(X: np.ndarray, k: int) -> KMeans:
    return KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)


def fit_dbscan(X: np.ndarray, eps: float = 0.5, min_samples: int = 5) -> DBSCAN:
    return DBSCAN(eps=eps, min_samples=min_samples).fit(X)


def scale_features(X: np.ndarray) -> tuple[np.ndarray, StandardScaler]:
    scaler = StandardScaler()
    return scaler.fit_transform(X), scaler
