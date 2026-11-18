"""Paired bootstrap CIs and Wilcoxon signed-rank vs a reference method."""

from __future__ import annotations

import numpy as np


def bootstrap_ci(values: np.ndarray, n_boot: int = 10000, seed: int = 0, stat=np.mean):
    v = np.asarray(values, float)
    if v.size == 0:
        return float("nan"), float("nan")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, v.size, size=(n_boot, v.size))
    s = stat(v[idx], axis=1)
    return float(np.percentile(s, 2.5)), float(np.percentile(s, 97.5))


def paired_compare(k_true, k_a, k_b, n_boot: int = 10000, seed: int = 0) -> dict:
    """Method a vs reference b over the same recordings. Differences are a - b."""
    t, a, b = (np.asarray(x, float) for x in (k_true, k_a, k_b))
    ea, eb = np.abs(a - t), np.abs(b - t)
    xa, xb = (ea == 0).astype(float), (eb == 0).astype(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, t.size, size=(n_boot, t.size))
    d_mae = ea[idx].mean(1) - eb[idx].mean(1)
    d_exact = xa[idx].mean(1) - xb[idx].mean(1)
    try:
        from scipy.stats import wilcoxon

        p = float(wilcoxon(ea, eb, zero_method="wilcox").pvalue) if np.any(ea != eb) else 1.0
    except ValueError:
        p = 1.0
    return {
        "d_mae": float(ea.mean() - eb.mean()),
        "d_mae_ci": (float(np.percentile(d_mae, 2.5)), float(np.percentile(d_mae, 97.5))),
        "d_exact": float(xa.mean() - xb.mean()),
        "d_exact_ci": (float(np.percentile(d_exact, 2.5)), float(np.percentile(d_exact, 97.5))),
        "wilcoxon_p": p,
        "n": int(t.size),
    }
