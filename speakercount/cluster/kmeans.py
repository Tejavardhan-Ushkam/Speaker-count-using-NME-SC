from __future__ import annotations

import numpy as np


def kmeans(x: np.ndarray, k: int, n_init: int = 10, seed: int = 0) -> np.ndarray:
    if k <= 1 or x.shape[0] <= 1:
        return np.zeros(x.shape[0], dtype=np.int64)
    from sklearn.cluster import KMeans

    k = min(k, x.shape[0])
    return KMeans(n_clusters=k, n_init=n_init, random_state=seed).fit_predict(x).astype(np.int64)


def relabel_by_size(labels: np.ndarray) -> np.ndarray:
    """Map labels to 0..K-1, largest cluster first (deterministic)."""
    uniq, counts = np.unique(labels, return_counts=True)
    order = uniq[np.lexsort((uniq, -counts))]
    mapping = {old: new for new, old in enumerate(order)}
    return np.array([mapping[v] for v in labels], dtype=np.int64)


def cluster_shares(labels: np.ndarray) -> np.ndarray:
    if labels.size == 0:
        return np.zeros(0)
    _, counts = np.unique(labels, return_counts=True)
    return np.sort(counts / labels.size)[::-1]
