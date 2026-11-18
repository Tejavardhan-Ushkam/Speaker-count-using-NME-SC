"""Graph Laplacians (dense torch and sparse scipy)."""

from __future__ import annotations

import numpy as np
import scipy.sparse as sp
import torch


def laplacian(w: torch.Tensor, kind: str) -> torch.Tensor:
    """unnormalized: L = D - W ; sym_norm: I - D^-1/2 W D^-1/2."""
    deg = w.sum(dim=1)
    if kind == "unnormalized":
        return torch.diag(deg) - w
    inv = deg.clamp_min(1e-12).rsqrt()
    return torch.eye(w.shape[0], dtype=w.dtype, device=w.device) - w * inv[:, None] * inv[None, :]


def laplacian_sparse(w: sp.spmatrix, kind: str) -> sp.csr_matrix:
    w = sp.csr_matrix(w)
    deg = np.asarray(w.sum(axis=1)).ravel()
    if kind == "unnormalized":
        return (sp.diags(deg) - w).tocsr()
    inv = 1.0 / np.sqrt(np.maximum(deg, 1e-12))
    d = sp.diags(inv)
    return (sp.identity(w.shape[0], format="csr") - d @ w @ d).tocsr()
