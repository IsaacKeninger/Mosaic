"""PCA dimensionality reduction for 2D visualization coordinates."""
import numpy as np
from sklearn.decomposition import PCA


def fit_pca(X: np.ndarray) -> PCA:
    """Fit a 2-component PCA on the scaled feature matrix. Kept (not just the
    transformed output) so new users can later be projected into the same space."""
    return PCA(n_components=2, random_state=42).fit(X)


def compute_pca_coordinates(X: np.ndarray) -> np.ndarray:
    """Reduce the scaled feature matrix to 2 components for scatter plotting."""
    return fit_pca(X).transform(X)
