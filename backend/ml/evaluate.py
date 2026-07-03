"""Model evaluation: elbow method, silhouette score, Davies-Bouldin index."""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score


def elbow_method(X: np.ndarray, k_range: range = range(2, 11)) -> dict[int, float]:
    """Return inertia for each K in k_range to help choose the optimal K."""
    inertias = {}
    for k in k_range:
        model = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
        inertias[k] = model.inertia_
    return inertias


def evaluate_clustering(X: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    """Compute silhouette score (target > 0.35) and Davies-Bouldin index."""
    return {
        "silhouette_score": silhouette_score(X, labels),
        "davies_bouldin_score": davies_bouldin_score(X, labels),
    }
