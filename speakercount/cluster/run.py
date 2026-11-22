"""Cluster one split with one method: affinity -> NME-SC p* -> backend -> post-processing.

Per recording, writes `<results>/recs/{rec}.npz` with everything in prompt §4.4 plus the
pre-post-processing labels and the embeddings z, so `tune` can re-apply post-processing cheaply.
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import torch
import yaml
from scipy.sparse.csgraph import connected_components

from ..config import Cfg, resolve_path, results_dir, write_run_metadata
from ..embedding import resolve_device
from ..pipeline import Session, load_split
from ..rttm import mode_k
from .kmeans import cluster_shares, kmeans, relabel_by_size
from .nmesc import binarize, eigengap_stats, exact_backend, search_p
from .postprocess import postprocess


def rec_file(cfg: Cfg, rec: str) -> Path:
    return results_dir(cfg) / "recs" / f"{rec}.npz"


def tuned_postprocess(cfg: Cfg) -> dict:
    """min_cluster_share / merge_threshold / single_speaker_threshold actually used."""
    pp = cfg.postprocess
    vals = {"min_cluster_share": pp.min_cluster_share, "merge_threshold": pp.merge_threshold,
            "single_speaker_threshold": pp.single_speaker_threshold, "share_mode": pp.share_mode,
            "p_min": None, "k_max": None, "source": "config"}
    if pp.enabled and pp.tuned_file:
        f = resolve_path(pp.tuned_file)
        if f.exists():
            best = yaml.safe_load(f.read_text())
            for k in ("min_cluster_share", "merge_threshold", "single_speaker_threshold"):
                vals[k] = best[k]
            vals["share_mode"] = best.get("share_mode", "absolute")   # older best.yaml files: absolute
            vals["p_min"] = best.get("p_min")                          # tuned NME-SC lower bound on p
            vals["k_max"] = best.get("k_max")                          # tuned cap on K (scope experiments)
            vals["source"] = str(pp.tuned_file)
        elif cfg.dataset.role == "test":
            raise FileNotFoundError(f"{f} missing: run `python run.py tune --method {cfg.method.name}` first")
        else:
            print(f"WARNING: {f} missing, using config post-processing values")
    return vals


class Embedder:
    """Maps a session to the embedding space whose cosine is the affinity."""

    def __init__(self, cfg: Cfg):
        self.cfg = cfg
        self.source = cfg.affinity.source
        self._model = None

    def __call__(self, sess: Session) -> np.ndarray:
        if self.source == "ecapa":
            z = sess.x
        elif self.source == "affnet":
            from ..affinity.infer import AffnetInference

            if self._model is None:
                self._model = AffnetInference(self.cfg)
            z = self._model(sess.x, sess.center)
        elif self.source == "siamese":
            from ..affinity.siamese import SiameseInference

            if self._model is None:
                self._model = SiameseInference(self.cfg)
            z = self._model(sess.x)
        else:
            raise ValueError(self.source)
        z = np.asarray(z, dtype=np.float32)
        return z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)


def cluster_session(sess: Session, z: np.ndarray, cfg: Cfg, pp_vals: dict) -> dict:
    c = cfg.clustering
    t0 = time.time()
    device = resolve_device(c.device)
    dtype = torch.float64 if c.dtype == "float64" else torch.float32
    n_all = sess.n
    keep = np.ones(n_all, dtype=bool)
    if cfg.affinity.oracle_overlap_removal:  # ORACLE ablation (uses reference labels)
        keep = ~sess.ambiguous
        if keep.sum() < 2:
            keep[:] = True
    zk = z[keep]
    n = int(zk.shape[0])
    out: dict = {"n_segments": n_all, "n_used": n, "keep": keep}

    zt = torch.as_tensor(zk, dtype=torch.float32, device=device)
    aff = zt @ zt.T
    mean_cos = float((aff.sum() - aff.diagonal().sum()) / max(1, n * (n - 1))) if n > 1 else float("nan")
    out["mean_cosine"] = mean_cos

    gap_cap = min(c.k_max, max(1, n - 1))
    if n < max(2, c.min_segments):
        labels_k = np.zeros(n, dtype=np.int64)
        out.update(k_eigengap=1, p_star=0, r_values=np.zeros(0), p_grid=np.zeros(0), eigenvalues=np.zeros(0),
                   eigengaps=np.zeros(0), gap_ratio=float("inf"), second_best_k=1, n_components=1)
    else:
        aff = aff.to(dtype)
        if cfg.affinity.refine:
            from .refine import refine_affinity

            aff = refine_affinity(aff, cfg.affinity.refine_blur_sigma, cfg.affinity.refine_percentile,
                                  cfg.affinity.refine_multiplier)
        if c.zero_diagonal:
            aff.fill_diagonal_(0.0)
        sr = search_p(aff, c)
        w = binarize(sr.order, sr.p_star, n, dtype, device)
        out["n_components"] = int(connected_components((w > 0).cpu().numpy(), directed=False, return_labels=False))
        out["time_search_sec"] = sr.timings["search_sec"]
        out["n_eig_fallback"] = sr.n_eig_fallback
        t1 = time.time()
        exact_vals, vecs = exact_backend(w, c)
        k_exact, gaps_exact, _, _ = eigengap_stats(exact_vals, gap_cap)
        out["time_exact_sec"] = time.time() - t1
        if c.backend == "spectralnet":
            from .spectralnet import fit_spectralnet

            t2 = time.time()
            snet = fit_spectralnet(zk, w, cfg, seed=cfg.seed)
            vals, spec = snet["ritz"], snet["Y"]
            k, gaps, ratio, k2 = eigengap_stats(vals, gap_cap)
            m = min(len(vals), len(exact_vals), c.k_max + 1)
            rel = np.abs(vals[:m] - exact_vals[:m]) / np.maximum(np.abs(exact_vals[:m]), 1e-6 * max(1.0, abs(exact_vals[m - 1])))
            out.update(time_snet_sec=time.time() - t2, snet_steps=snet["steps"], snet_k_exact=k_exact,
                       snet_exact_agree=int(k == k_exact), snet_ritz_max_relerr=float(rel[1:].max() if m > 1 else 0.0),
                       exact_eigenvalues=exact_vals[: c.k_max + 5])
            feats = spec[:, :k]
            feats = feats / np.maximum(np.linalg.norm(feats, axis=1, keepdims=True), 1e-12)
        else:
            vals = exact_vals
            k, gaps, ratio, k2 = eigengap_stats(vals, gap_cap)
            feats = vecs[:, :k].double().cpu().numpy()
        labels_k = kmeans(feats, k, c.kmeans_n_init, cfg.seed)
        out.update(k_eigengap=k, p_star=sr.p_star, p_max=sr.p_max, r_values=sr.r_values, p_grid=sr.p_grid,
                   eigenvalues=vals[: c.k_max + 5], eigengaps=gaps, gap_ratio=ratio, second_best_k=k2)

    labels_raw = relabel_by_size(labels_k)
    if cfg.postprocess.enabled:
        labels_pp, info = postprocess(labels_raw, zk, mean_cos, pp_vals["min_cluster_share"],
                                      pp_vals["merge_threshold"], pp_vals["single_speaker_threshold"],
                                      pp_vals.get("share_mode", "absolute"))
        out.update(pp_pruned=info["pruned"], pp_merged=info["merged"], pp_single=int(info["single_speaker"]))
    else:
        labels_pp = labels_raw
    # oracle-removal ablation: give removed segments the nearest centroid's label (for DER only)
    labels_full = np.zeros(n_all, dtype=np.int64)
    labels_full[keep] = labels_pp
    raw_full = np.zeros(n_all, dtype=np.int64)
    raw_full[keep] = labels_raw
    if not keep.all():
        ids = np.unique(labels_pp)
        cent = np.stack([zk[labels_pp == i].mean(0) for i in ids])
        labels_full[~keep] = ids[np.argmax(z[~keep] @ cent.T, axis=1)]
    out["labels"] = labels_full
    out["labels_raw"] = raw_full
    out["k_pred"] = int(np.unique(labels_pp).size)
    shares = cluster_shares(labels_pp)
    out["cluster_sizes"] = shares
    out["time_cluster_sec"] = time.time() - t0
    return out


def _row(sess: Session, res: dict, k_max: int) -> dict:
    shares = res.get("cluster_sizes", np.zeros(0))
    return {
        "recording_id": sess.rec,
        "k_true": sess.meta["k_true"],
        "k_pred": res["k_pred"],
        "k_eigengap": res.get("k_eigengap", res["k_pred"]),
        "p_star": res.get("p_star", 0),
        "gap_ratio": res.get("gap_ratio", float("nan")),
        "second_best_k": res.get("second_best_k", 0),
        "smallest_cluster_share": float(shares.min()) if shares.size else float("nan"),
        "largest_cluster_share": float(shares.max()) if shares.size else float("nan"),
        "n_segments": sess.n,
        "n_ambiguous_segments": int(sess.ambiguous.sum()),
        "mean_cosine": res.get("mean_cosine", float("nan")),
        "saturated": int(res["k_pred"] >= k_max or res.get("k_eigengap", 0) >= k_max),
        "duration_sec": sess.meta["duration_sec"],
        "speech_sec": sess.meta["speech_sec"],
        "cluster_sec": res.get("time_cluster_sec", 0.0),
        "n_components": res.get("n_components", 0),
        "snet_exact_agree": res.get("snet_exact_agree", ""),
        "snet_ritz_max_relerr": res.get("snet_ritz_max_relerr", ""),
        "snet_ritz_scaled_err": _scaled_err(res, k_max),
    }


def _scaled_err(res: dict, k_max: int):
    """max_i |ritz_i - exact_i| / exact_{k_max+1}: error relative to the spectrum's scale
    (plain relative error explodes on the near-zero within-cluster eigenvalues)."""
    if "exact_eigenvalues" not in res:
        return ""
    r, e = np.asarray(res["eigenvalues"]), np.asarray(res["exact_eigenvalues"])
    m = min(len(r), len(e), k_max + 1)
    return float(np.max(np.abs(r[:m] - e[:m])) / max(abs(e[m - 1]), 1e-12)) if m else ""


def _save(cfg: Cfg, rec: str, res: dict, z: np.ndarray) -> None:
    f = rec_file(cfg, rec)
    f.parent.mkdir(parents=True, exist_ok=True)
    arrays = {k: np.asarray(v) for k, v in res.items() if v is not None and not isinstance(v, str)}
    arrays["z"] = z.astype(np.float16)
    tmp = f.with_name(f.stem + ".partial.npz")   # atomic: a killed run never leaves a truncated cache file
    np.savez_compressed(tmp, **arrays)
    tmp.replace(f)


def load_rec(cfg: Cfg, rec: str) -> dict:
    with np.load(rec_file(cfg, rec)) as d:
        return {k: (d[k].item() if d[k].ndim == 0 else d[k]) for k in d.files}


def cluster_split(cfg: Cfg, only=None, force: bool = False) -> list[dict]:
    out = results_dir(cfg)
    write_run_metadata(cfg, out)
    sessions = load_split(cfg, only)
    rows = []
    t0 = time.time()
    pp_vals = tuned_postprocess(cfg) if cfg.clustering.backend != "none" else {}
    if pp_vals.get("k_max") is not None:   # tuned together with the post-processing (tune.py)
        cfg.clustering.k_max = int(pp_vals["k_max"])
    k_max = cfg.clustering.k_max
    if cfg.clustering.backend == "none":  # baseline_mode
        k = mode_k(cfg)
        for s in sessions:
            res = {"k_pred": k, "k_eigengap": k, "labels": np.zeros(s.n, dtype=np.int64)}
            rows.append(_row(s, res, k_max) | {"smallest_cluster_share": float("nan"),
                                                "largest_cluster_share": float("nan")})
        print(f"[cluster {cfg.method.name}] baseline_mode predicts K={k} for {len(sessions)} recordings")
        return rows
    if pp_vals.get("p_min") is not None:   # tuned together with the post-processing (tune.py)
        cfg.clustering.p_min = int(pp_vals["p_min"])
    if pp_vals.get("p_min") is not None or pp_vals.get("k_max") is not None:
        write_run_metadata(cfg, out)       # re-write so config_resolved.yaml shows the values actually used
    (out / "postprocess_used.yaml").write_text(yaml.safe_dump(pp_vals, sort_keys=False))
    emb = Embedder(cfg)
    for i, s in enumerate(sessions, 1):
        if not force and rec_file(cfg, s.rec).exists():
            res = load_rec(cfg, s.rec)
        else:
            z = emb(s)
            res = cluster_session(s, z, cfg, pp_vals)
            _save(cfg, s.rec, res, z)
            print(f"[cluster {cfg.dataset.corpus}/{cfg.dataset.split}/{cfg.method.name}] {i}/{len(sessions)} "
                  f"{s.rec}: N={s.n} K={s.meta['k_true']} K^={res['k_pred']} (eigengap {res.get('k_eigengap')}) "
                  f"p*={res.get('p_star')} {res['time_cluster_sec']:.1f}s", flush=True)
        rows.append(_row(s, res, k_max))
    print(f"[cluster {cfg.method.name}] {len(sessions)} recordings in {time.time() - t0:.1f} s")
    return rows
