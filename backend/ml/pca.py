"""PCA dimensionality reduction for 2D visualization coordinates."""
import numpy as np
from sklearn.decomposition import PCA


def compute_pca_coordinates(X: np.ndarray) -> np.ndarray:
    """Reduce the scaled feature matrix to 2 components for scatter plotting."""
    return PCA(n_components=2, random_state=42).fit_transform(X)
