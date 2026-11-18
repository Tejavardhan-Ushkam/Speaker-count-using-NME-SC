"""NME-SC (Park et al. 2020), fast version.

Changes vs the old project (prompt §4.4):
  * p_max = min(floor(0.25 N), p_max_abs)            (p_max_abs=None -> old behaviour)
  * coarse-to-fine p search: stride-4 grid, then stride 1 within +-4 of the best coarse p
  * during the search only the smallest k_max+1 eigenvalues (+ lambda_max) are computed with
    scipy eigsh (shift-invert) on the sparse Laplacian; dense eigvalsh is the fallback.
The count at p* and its eigenvectors come from one dense eigh ("exact backend").
"""

from __future__ import annotations

import math
import time
import warnings
from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp
import torch

from .laplacian import laplacian, laplacian_sparse


@dataclass
class SearchResult:
    p_star: int
    p_grid: np.ndarray                 # every p evaluated (in evaluation order)
    r_values: np.ndarray               # r(p) for p_grid
    order: torch.Tensor                # (N, p_max) top-k neighbour indices
    p_max: int
    n_eig_fallback: int = 0
    timings: dict = field(default_factory=dict)


def p_max_for(n: int, c) -> int:
    p_max = int(math.floor(n * c.p_max_ratio))
    if c.p_max_abs is not None:
        p_max = min(p_max, int(c.p_max_abs))
    return max(c.p_min, min(p_max, n - 1))


def binarize(order: torch.Tensor, p: int, n: int, dtype, device) -> torch.Tensor:
    """Dense symmetric 0.5 (B + B^T) with B the row-wise top-p mask."""
    b = torch.zeros((n, n), dtype=dtype, device=device)
    b.scatter_(1, order[:, :p], 1.0)
    return 0.5 * (b + b.T)


def binarize_sparse(order_np: np.ndarray, p: int, n: int) -> sp.csr_matrix:
    rows = np.repeat(np.arange(n), p)
    cols = order_np[:, :p].ravel()
    b = sp.csr_matrix((np.ones(rows.size), (rows, cols)), shape=(n, n))
    return (0.5 * (b + b.T)).tocsr()


def _r_from_eigs(small: np.ndarray, lam_max: float, p: int, gap_cap: int, eps: float) -> float:
    gaps = np.diff(small)[:gap_cap]
    g = float(gaps.max()) / (lam_max + eps)
    return float(p) / (g + eps)


class _SparseMismatch(RuntimeError):
    pass


def _eigs_sparse(w: sp.csr_matrix, kind: str, k: int):
    """Smallest k eigenvalues and lambda_max of L(w), component-aware.

    The multiplicity of eigenvalue 0 equals the number of connected components c (exact,
    from a graph traversal). If c >= k the k smallest eigenvalues are exactly 0 and no
    eigensolver is needed; otherwise shift-invert eigsh is run and its zero count is checked
    against c (ARPACK can drop copies of a degenerate eigenvalue) -> mismatch = dense fallback.
    """
    from scipy.sparse.csgraph import connected_components
    from scipy.sparse.linalg import eigsh

    n = w.shape[0]
    lap = laplacian_sparse(w, kind)
    rng = np.random.default_rng(0)
    v0 = rng.standard_normal(n)
    big = float(eigsh(lap, k=1, which="LA", v0=v0, return_eigenvectors=False, tol=1e-6)[0])
    n_comp = int(connected_components(w, directed=False, return_labels=False))
    if n_comp >= k:
        return np.zeros(k), big
    small = np.sort(eigsh(lap, k=k, sigma=-1e-2, which="LM", v0=v0, return_eigenvectors=False, tol=1e-10))
    zero_tol = 1e-6 * max(1.0, big)
    if int(np.sum(np.abs(small) < zero_tol)) != n_comp:
        raise _SparseMismatch(f"eigsh zero count != {n_comp} components")
    small[:n_comp] = 0.0
    return small, big


def _eigs_dense(w: torch.Tensor, kind: str, k: int):
    ev = torch.linalg.eigvalsh(laplacian(w, kind))
    ev = ev.double().cpu().numpy()
    return ev[:k], float(ev[-1])


def search_p(aff: torch.Tensor, c, solver: str | None = None) -> SearchResult:
    """Find p* = argmin_p p / g(p) on the (coarse-to-fine) grid."""
    n = aff.shape[0]
    solver = solver or c.eig_solver
    p_max = p_max_for(n, c)
    gap_cap = min(c.k_max, n - 1)
    k_eig = min(gap_cap + 1, n)
    t0 = time.time()
    _, order = torch.topk(aff, k=p_max, dim=1)
    order_np = order.cpu().numpy()
    fallback = 0
    cache: dict[int, float] = {}

    def r_of(p: int) -> float:
        nonlocal fallback
        if p in cache:
            return cache[p]
        small = lam_max = None
        # sparse eigsh only pays off for large N; tiny graphs go straight to dense
        if solver == "sparse" and n > 4 * k_eig + 50:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    small, lam_max = _eigs_sparse(binarize_sparse(order_np, p, n), c.laplacian, k_eig)
            except Exception:  # noqa: BLE001 - ArpackNoConvergence, singular factor, ...
                fallback += 1
                small = None
        if small is None:
            w = binarize(order, p, n, aff.dtype, aff.device)
            small, lam_max = _eigs_dense(w, c.laplacian, k_eig)
        cache[p] = _r_from_eigs(small, lam_max, p, gap_cap, c.eps)
        return cache[p]

    if c.coarse_to_fine and p_max - c.p_min + 1 > 2 * c.coarse_stride:
        coarse = list(range(c.p_min, p_max + 1, c.coarse_stride))
        if coarse[-1] != p_max:
            coarse.append(p_max)
        best_c = min(coarse, key=lambda p: (r_of(p), p))
        lo, hi = max(c.p_min, best_c - c.fine_radius), min(p_max, best_c + c.fine_radius)
        for p in range(lo, hi + 1):
            r_of(p)
    else:
        for p in range(c.p_min, p_max + 1):
            r_of(p)
    grid = np.array(sorted(cache), dtype=np.int64)
    r = np.array([cache[p] for p in grid])
    p_star = int(grid[int(np.argmin(r))])  # argmin returns the smallest p on ties, as the old code
    return SearchResult(p_star, grid, r, order, p_max, fallback, {"search_sec": time.time() - t0})


def eigengap_stats(eigs: np.ndarray, gap_cap: int):
    """K = argmax eigengap over the first gap_cap gaps; also gap ratio and runner-up K."""
    gaps = np.diff(eigs)[:gap_cap]
    if gaps.size == 0:
        return 1, gaps, float("inf"), 1
    idx = np.argsort(-gaps, kind="stable")
    k = int(idx[0]) + 1
    if gaps.size > 1:
        second = gaps[idx[1]]
        ratio = float(gaps[idx[0]] / second) if second > 0 else float("inf")
        k2 = int(idx[1]) + 1
    else:
        ratio, k2 = float("inf"), k
    return k, gaps, ratio, k2


def exact_backend(w: torch.Tensor, c):
    """Dense eigh at p*: eigenvalues, eigenvectors, K."""
    lap = laplacian(w, c.laplacian)
    vals, vecs = torch.linalg.eigh(lap)
    return vals.double().cpu().numpy(), vecs
