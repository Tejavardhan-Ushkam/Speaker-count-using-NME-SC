"""SpectralNet v2: orthonormality, Ritz values vs exact eigh on a synthetic graph."""

from __future__ import annotations

import numpy as np
import torch

from speakercount.config import load_config
from speakercount.cluster.laplacian import laplacian
from speakercount.cluster.nmesc import binarize, eigengap_stats, search_p
from speakercount.cluster.spectralnet import fit_spectralnet, orthonorm_factor, transform


def _graph(k=4, n_per=80, seed=0, noise=0.5):
    rng = np.random.default_rng(seed)
    c = rng.standard_normal((k, 32))
    z = np.concatenate([c[i] + noise * rng.standard_normal((n_per, 32)) for i in range(k)])
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    return z


def _cfg():
    cfg = load_config("configs/ami_dev.yaml")
    cfg.clustering.device = "cpu"
    cfg.spectralnet.device = "cpu"
    cfg.spectralnet.warm_start = False
    return cfg


def test_orthonorm_factor():
    y = torch.randn(500, 11, dtype=torch.float64)
    r = orthonorm_factor(y, 1e-6)
    g = (y @ r).T @ (y @ r) / 500
    assert torch.allclose(g, torch.eye(11, dtype=torch.float64), atol=1e-6)


def test_ritz_matches_eigh_on_synthetic_graph():
    cfg = _cfg()
    for k in (2, 4, 7):
        z = _graph(k, seed=k)
        a = torch.as_tensor(z @ z.T)
        a.fill_diagonal_(0)
        sr = search_p(a, cfg.clustering)
        w = binarize(sr.order, sr.p_star, len(z), a.dtype, a.device)
        exact = torch.linalg.eigvalsh(laplacian(w, cfg.clustering.laplacian)).numpy()
        fit = fit_spectralnet(z, w, cfg)
        ritz = fit["ritz"]
        m = cfg.clustering.k_max + 1
        # compare the k_max+1 smallest; eigenvalues that are exactly 0 are compared absolutely
        scale = max(1.0, exact[m - 1])
        rel = np.abs(ritz[:m] - exact[:m]) / np.maximum(exact[:m], 1e-3 * scale)
        assert eigengap_stats(ritz, cfg.clustering.k_max)[0] == k == eigengap_stats(exact, cfg.clustering.k_max)[0]
        assert rel[k:].max() < 1e-2 or np.abs(ritz[:m] - exact[:m]).max() < 1e-2 * scale, (k, rel)
        # frozen map reproduces Y on the training segments
        assert np.allclose(transform(fit, z), fit["Y"], atol=1e-6)
