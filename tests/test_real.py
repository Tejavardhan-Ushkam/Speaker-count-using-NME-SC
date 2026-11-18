"""Checks on real cached AMI recordings (skipped if `prepare` has not been run)."""

from __future__ import annotations

import numpy as np
import torch

from speakercount.config import load_config
from speakercount.cluster.nmesc import binarize, eigengap_stats, exact_backend, search_p
from speakercount.pipeline import emb_file, load_session

RECS = ("EN2002a", "IS1009a", "TS3003a")


def _skip_if_missing(cfg):
    if not all(emb_file(cfg, r).exists() for r in RECS):
        from tests.run_tests import skip

        skip("AMI test not prepared")


def _run(x, c, dtype):
    a = torch.as_tensor(x @ x.T, dtype=dtype)
    a.fill_diagonal_(0.0)
    sr = search_p(a, c)
    w = binarize(sr.order, sr.p_star, a.shape[0], dtype, a.device)
    vals, _ = exact_backend(w, c)
    return sr.p_star, eigengap_stats(vals, c.k_max)[0]


def test_sparse_vs_dense_on_three_recordings():
    cfg = load_config("configs/ami_test.yaml")
    _skip_if_missing(cfg)
    c = cfg.clustering
    c.device = "cpu"
    for rec in RECS:
        x = load_session(cfg, rec).x.astype(np.float64)
        c.eig_solver = "dense"
        d = _run(x, c, torch.float64)
        c.eig_solver = "sparse"
        s = _run(x, c, torch.float64)
        assert d == s, (rec, d, s)


def test_float32_vs_float64_same_k():
    cfg = load_config("configs/ami_test.yaml")
    _skip_if_missing(cfg)
    c = cfg.clustering
    c.device = "cpu"
    c.eig_solver = "dense"
    for rec in RECS:
        x = load_session(cfg, rec).x
        k32 = _run(x.astype(np.float32), c, torch.float32)[1]
        k64 = _run(x.astype(np.float64), c, torch.float64)[1]
        assert k32 == k64, (rec, k32, k64)
