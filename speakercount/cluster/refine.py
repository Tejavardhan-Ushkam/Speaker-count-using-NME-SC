"""Affinity refinement ops of Wang et al. 2018 (ablation, off by default; prompt §4.7)."""

from __future__ import annotations

import torch


def refine_affinity(a: torch.Tensor, sigma: float = 1.0, percentile: float = 95.0, mult: float = 0.01) -> torch.Tensor:
    """Gaussian blur -> row-wise threshold -> symmetrise (max) -> diffusion -> row-max normalise.
    Rows/cols are assumed time-ordered (segments are stored in time order)."""
    # 1. Gaussian blur (separable, sigma in matrix cells)
    if sigma > 0:
        r = max(1, int(round(3 * sigma)))
        x = torch.arange(-r, r + 1, dtype=a.dtype, device=a.device)
        k = torch.exp(-0.5 * (x / sigma) ** 2)
        k = (k / k.sum()).view(1, 1, -1)
        m = a.unsqueeze(1)                                       # (N,1,N): blur along columns
        m = torch.nn.functional.conv1d(m, k, padding=r).squeeze(1)
        m = torch.nn.functional.conv1d(m.T.unsqueeze(1), k, padding=r).squeeze(1).T
        a = m
    # 2. row-wise thresholding: keep values >= row percentile, multiply the rest by mult
    # (kthvalue, not torch.quantile: quantile refuses inputs > 2^24 elements)
    kth = min(a.shape[1], max(1, int(round(percentile / 100.0 * a.shape[1]))))
    thr = a.kthvalue(kth, dim=1, keepdim=True).values
    a = torch.where(a >= thr, a, a * mult)
    # 3. symmetrise (max)
    a = torch.maximum(a, a.T)
    # 4. diffusion
    a = a @ a.T
    # 5. row-max normalisation
    a = a / a.max(dim=1, keepdim=True).values.clamp_min(1e-12)
    return a
