"""Counting metrics, per-K-bin breakdown, confusion, cluster health."""

from __future__ import annotations

import numpy as np
import pandas as pd

K_BINS = [(1, 1, "1"), (2, 2, "2"), (3, 3, "3"), (4, 4, "4"), (5, 7, "5-7"), (8, 12, "8-12"), (13, 10**6, "13+")]


def k_bin(k: int) -> str:
    for lo, hi, name in K_BINS:
        if lo <= k <= hi:
            return name
    return "?"


def count_metrics(k_true, k_pred, tau: float = 0.15) -> dict:
    t = np.asarray(k_true, float)
    p = np.asarray(k_pred, float)
    if t.size == 0:
        return {}
    err = p - t
    rel = np.abs(err) / t
    return {
        "n": int(t.size),
        "exact": float(np.mean(err == 0)),
        "within1": float(np.mean(np.abs(err) <= 1)),
        "mae": float(np.mean(np.abs(err))),
        "signed": float(np.mean(err)),
        "rel_acc": float(np.mean(rel <= tau + 1e-12)),
        "rel_err_mean": float(np.mean(rel)),
        "rel_err_median": float(np.median(rel)),
    }


def per_bin(df: pd.DataFrame, tau: float = 0.15) -> pd.DataFrame:
    rows = []
    for _, _, name in K_BINS:
        sub = df[df.k_true.map(k_bin) == name]
        if len(sub):
            rows.append({"bin": name, **count_metrics(sub.k_true, sub.k_pred, tau)})
    return pd.DataFrame(rows)


def confusion(df: pd.DataFrame) -> pd.DataFrame:
    return pd.crosstab(df.k_true, df.k_pred, rownames=["K"], colnames=["K^"])


def cluster_health(df: pd.DataFrame, k_max: int) -> dict:
    return {
        "smallest<3%": int((df.smallest_cluster_share < 0.03).sum()),
        "largest>80%": int((df.largest_cluster_share > 0.80).sum()),
        "K^=k_max": int((df.k_pred >= k_max).sum()),
        "eigengap K=k_max": int((df.k_eigengap >= k_max).sum()),
        "gap_ratio<1.5": int((df.gap_ratio < 1.5).sum()),
    }
