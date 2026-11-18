"""NME-SC on synthetic block-diagonal affinities, dense vs sparse eigen agreement,
post-processing on toy clusters, DER = 0 for hyp == ref."""

from __future__ import annotations

import numpy as np
import torch

from speakercount.config import load_config
from speakercount.cluster.kmeans import relabel_by_size
from speakercount.cluster.nmesc import binarize, eigengap_stats, exact_backend, search_p
from speakercount.cluster.postprocess import postprocess


def _clustering_cfg(**kw):
    c = load_config("configs/ami_test.yaml").clustering
    c.device = "cpu"
    c.dtype = "float64"
    for k, v in kw.items():
        c[k] = v
    return c


def _blocks(k: int, n_per: int = 60, dim: int = 32, noise: float = 0.15, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    centers = rng.standard_normal((k, dim))
    x = np.concatenate([centers[i] + noise * rng.standard_normal((n_per, dim)) for i in range(k)])
    return x / np.linalg.norm(x, axis=1, keepdims=True)


def _count(x: np.ndarray, c):
    a = torch.as_tensor(x @ x.T, dtype=torch.float64)
    a.fill_diagonal_(0.0)
    sr = search_p(a, c)
    w = binarize(sr.order, sr.p_star, a.shape[0], a.dtype, a.device)
    vals, _ = exact_backend(w, c)
    k, *_ = eigengap_stats(vals, min(c.k_max, a.shape[0] - 1))
    return k, sr.p_star


def test_nmesc_block_diagonal_known_k():
    c = _clustering_cfg()
    for k in (2, 4, 7):
        got, _ = _count(_blocks(k, seed=k), c)
        assert got == k, (k, got)


def test_dense_vs_sparse_same_pstar_and_k():
    for k in (2, 4, 7):
        x = _blocks(k, n_per=80, noise=0.6, seed=10 + k)
        kd, pd_ = _count(x, _clustering_cfg(eig_solver="dense"))
        ks, ps = _count(x, _clustering_cfg(eig_solver="sparse"))
        assert (kd, pd_) == (ks, ps), (k, kd, pd_, ks, ps)


def test_coarse_to_fine_matches_full_sweep_on_easy_graph():
    x = _blocks(4, n_per=60, seed=3)
    k1, _ = _count(x, _clustering_cfg(coarse_to_fine=True))
    k2, _ = _count(x, _clustering_cfg(coarse_to_fine=False))
    assert k1 == k2 == 4


def test_postprocess_prune_and_merge():
    rng = np.random.default_rng(0)
    c = np.eye(4)
    z = np.concatenate([c[0] + 0.05 * rng.standard_normal((50, 4)),
                        c[1] + 0.05 * rng.standard_normal((40, 4)),
                        c[2] + 0.05 * rng.standard_normal((2, 4))])
    z /= np.linalg.norm(z, axis=1, keepdims=True)
    labels = np.array([0] * 50 + [1] * 40 + [2] * 2)
    out, info = postprocess(labels, z, 0.0, min_cluster_share=0.05)
    assert np.unique(out).size == 2 and info["pruned"] == 1
    # merge: split cluster 0 into two halves with identical centroids -> merged back
    labels2 = np.array([0] * 25 + [3] * 25 + [1] * 40 + [2] * 2)
    out2, info2 = postprocess(labels2, z, 0.0, min_cluster_share=0.0, merge_threshold=0.8)
    assert np.unique(out2).size == 3 and info2["merged"] == 1
    # never below 1 / single-speaker check
    out3, info3 = postprocess(labels, z, 0.9, min_cluster_share=0.9, single_speaker_threshold=0.5)
    assert np.unique(out3).size == 1 and info3["single_speaker"]


def test_relabel_by_size():
    assert relabel_by_size(np.array([5, 5, 2, 9, 9, 9])).tolist() == [1, 1, 2, 0, 0, 0]


def test_der_zero_for_identical_hypothesis():
    from speakercount.eval.der import der
    from speakercount.rttm import Turn

    ref = [Turn("r", 0, 5, "A"), Turn("r", 5, 3, "B"), Turn("r", 9, 4, "A")]
    hyp = [Turn("r", t.start, t.duration, {"A": "x", "B": "y"}[t.speaker]) for t in ref]
    assert der(ref, hyp)["der"] < 1e-9
    assert der(ref, hyp, skip_overlap=True)["der"] < 1e-9


def test_hyp_turns_nearest_centre():
    from speakercount.eval.der import hyp_turns

    start = np.array([0.0, 0.75, 1.5, 10.0])
    end = start + 1.5
    turns = hyp_turns("r", start, end, np.array([0, 0, 1, 1]))
    spk = [(round(t.start, 2), round(t.end, 2), t.speaker) for t in turns]
    # boundary between centres 1.5 (seg1) and 2.25 (seg2) -> 1.875 ; gap 3.0-10.0 uncovered
    assert spk[0][0] == 0.0 and abs(spk[0][1] - 1.88) < 0.011 and spk[0][2] == "spk00"
    assert spk[1][2] == "spk01" and abs(spk[1][1] - 3.0) < 0.011
    assert spk[2] == (10.0, 11.5, "spk01")
