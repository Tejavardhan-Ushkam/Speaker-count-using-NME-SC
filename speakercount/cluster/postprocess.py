"""Post-processing after any backend (prompt §4.6): prune tiny clusters, merge near-duplicate
centroids, never below K=1, single-speaker check."""

from __future__ import annotations

import numpy as np

from .kmeans import relabel_by_size


def _centroids(z: np.ndarray, labels: np.ndarray, ids: np.ndarray) -> np.ndarray:
    c = np.stack([z[labels == i].mean(axis=0) for i in ids])
    return c / np.maximum(np.linalg.norm(c, axis=1, keepdims=True), 1e-12)


def postprocess(labels: np.ndarray, z: np.ndarray, mean_cosine: float,
                min_cluster_share: float = 0.0, merge_threshold: float | None = None,
                single_speaker_threshold: float | None = None, share_mode: str = "absolute"):
    """Returns (labels relabelled 0..K-1 by size, info dict).

    share_mode "absolute": prune clusters with share < min_cluster_share (e.g. 0.02 = 2 % of segments).
    share_mode "relative": prune clusters with share < min_cluster_share / K_in, i.e. smaller than that
    fraction of the average cluster (K_in = clusters before pruning), so the threshold shrinks as K grows.
    """
    labels = np.asarray(labels, dtype=np.int64).copy()
    n = labels.size
    info = {"pruned": 0, "merged": 0, "single_speaker": False}
    if n == 0:
        return labels, info

    # 1. prune tiny clusters: dissolve, re-assign members to the nearest remaining centroid (cosine on z)
    if min_cluster_share and min_cluster_share > 0:
        ids, counts = np.unique(labels, return_counts=True)
        if share_mode not in ("absolute", "relative"):
            raise ValueError(f"share_mode must be absolute|relative, got {share_mode}")
        thr = min_cluster_share / ids.size if share_mode == "relative" else min_cluster_share
        info["prune_threshold"] = float(thr)
        keep = ids[counts / n >= thr]
        if keep.size == 0:  # never below K = 1: keep the largest
            keep = ids[[int(np.argmax(counts))]]
        drop = np.setdiff1d(ids, keep)
        if drop.size:
            cent = _centroids(z, labels, keep)
            moved = np.isin(labels, drop)
            labels[moved] = keep[np.argmax(z[moved] @ cent.T, axis=1)]
            info["pruned"] = int(drop.size)

    # 2. merge near-duplicate clusters while the highest centroid cosine > merge_threshold
    if merge_threshold is not None:
        while True:
            ids = np.unique(labels)
            if ids.size <= 1:
                break
            cent = _centroids(z, labels, ids)
            sim = cent @ cent.T
            np.fill_diagonal(sim, -np.inf)
            i, j = np.unravel_index(int(np.argmax(sim)), sim.shape)
            if sim[i, j] <= merge_threshold:
                break
            labels[labels == ids[j]] = ids[i]
            info["merged"] += 1

    # 4. single-speaker check
    if single_speaker_threshold is not None and np.isfinite(mean_cosine) and mean_cosine > single_speaker_threshold:
        labels[:] = 0
        info["single_speaker"] = True

    return relabel_by_size(labels), info
