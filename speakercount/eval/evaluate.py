"""`evaluate` = cluster + hypothesis RTTMs + DER + predictions.csv + summary.md ; `inspect`."""

from __future__ import annotations

import time

import numpy as np
import pandas as pd

from ..cluster.run import cluster_split, load_rec, rec_file
from ..config import Cfg, results_dir
from ..pipeline import load_session
from ..rttm import read_rttm, rttm_path, write_rttm
from .der import der, hyp_turns

COLUMNS = ["recording_id", "k_true", "k_pred", "k_eigengap", "p_star", "gap_ratio", "second_best_k",
           "smallest_cluster_share", "largest_cluster_share", "n_segments", "n_ambiguous_segments",
           "mean_cosine", "saturated", "duration_sec", "speech_sec", "cluster_sec", "der", "der_no_overlap",
           "snet_exact_agree"]


def evaluate(cfg: Cfg, force: bool = False) -> pd.DataFrame:
    t0 = time.time()
    rows = cluster_split(cfg, force=force)
    out = results_dir(cfg)
    hyp_dir = out / "hyp_rttm"
    for row in rows:
        rec = row["recording_id"]
        if cfg.clustering.backend == "none":
            row["der"] = row["der_no_overlap"] = float("nan")
            continue
        sess = load_session(cfg, rec)
        res = load_rec(cfg, rec)
        hyp = hyp_turns(rec, sess.start, sess.end, np.asarray(res["labels"]), cfg.evaluation.frame_step)
        write_rttm(hyp_dir / f"{rec}.rttm", hyp)
        ref = read_rttm(rttm_path(cfg, rec))
        d1 = der(ref, hyp, cfg.evaluation.collar, skip_overlap=False)
        d2 = der(ref, hyp, cfg.evaluation.collar, skip_overlap=True)
        row.update(der=d1["der"], der_miss=d1["miss"], der_fa=d1["fa"], der_conf=d1["conf"],
                   der_no_overlap=d2["der"])
    df = pd.DataFrame(rows)
    cols = COLUMNS + [c for c in df.columns if c not in COLUMNS]
    df = df.reindex(columns=cols)
    df.to_csv(out / "predictions.csv", index=False)
    print(f"[evaluate] wrote {out / 'predictions.csv'} ({time.time() - t0:.1f} s)")
    from .report import write_report

    write_report(cfg)
    return df


def inspect(cfg: Cfg, rec: str) -> None:
    if not rec_file(cfg, rec).exists():
        cluster_split(cfg, only=[rec])
    res = load_rec(cfg, rec)
    sess = load_session(cfg, rec)
    np.set_printoptions(precision=4, suppress=True, linewidth=140)
    print(f"recording {rec}: K_true={sess.meta['k_true']} N={sess.n} ambiguous={int(sess.ambiguous.sum())}")
    for k in ("k_pred", "k_eigengap", "p_star", "p_max", "gap_ratio", "second_best_k", "mean_cosine",
              "n_components", "time_cluster_sec", "time_search_sec", "snet_exact_agree", "snet_ritz_max_relerr",
              "pp_pruned", "pp_merged", "pp_single"):
        if k in res:
            print(f"  {k:22s} {res[k]}")
    print("  eigenvalues   ", np.asarray(res.get("eigenvalues", [])))
    if "exact_eigenvalues" in res:
        print("  exact eigvals ", np.asarray(res["exact_eigenvalues"]))
    print("  eigengaps     ", np.asarray(res.get("eigengaps", [])))
    print("  cluster sizes %", np.round(100 * np.asarray(res.get("cluster_sizes", [])), 1))
    # reference speaker composition of each predicted cluster (clean segments only)
    labels = np.asarray(res["labels"])
    ref = np.array([lab if lab is not None else "-" for lab in sess.label])
    tab = pd.crosstab(pd.Series(labels, name="cluster"), pd.Series(ref, name="ref speaker"))
    print(tab.to_string())
