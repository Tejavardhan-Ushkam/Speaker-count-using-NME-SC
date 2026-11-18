"""`tune`: post-processing grid search on the validation sets only (prompt §4.6).

1. Cluster each available val set once with the method's affinity/backend and *no*
   post-processing (tag `tuning_raw`); the per-recording npz keeps the raw labels and z.
2. Re-apply post-processing for every grid point (cheap) and score.

Objective = 0.5 * exact(AMI dev) + 0.5 * relative_accuracy(Vox val), ties -> lower mean MAE.
When a val set is unavailable its term is dropped and the remaining term gets weight 1
(AMI-only mode); the sets actually used are written to best.yaml.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import yaml

from .cluster.postprocess import postprocess
from .cluster.run import cluster_split, load_rec
from .config import ROOT, dump_yaml, git_commit, load_config
from .eval.metrics import count_metrics
from .rttm import available_configs


def _fmt(v):
    return "off" if v is None else v


def tune(method: str, overrides: list[str] | None = None) -> dict:
    base = load_config(None, method=method, overrides=overrides)
    if not base.postprocess.enabled:
        raise ValueError(f"{method} has no post-processing to tune")
    vals = available_configs(list(base.tuning.val_configs), "tune")
    raw_over = list(overrides or []) + ["method.tag=tuning_raw", "postprocess.tuned_file=null",
                                        "postprocess.min_cluster_share=0.0", "postprocess.merge_threshold=null",
                                        "postprocess.single_speaker_threshold=null"]
    data = {}
    for vc in vals:
        cfg = load_config(vc, method=method, overrides=raw_over)
        rows = cluster_split(cfg)
        recs = []
        for r in rows:
            d = load_rec(cfg, r["recording_id"])
            keep = np.asarray(d["keep"], bool)
            recs.append((r["k_true"], np.asarray(d["labels_raw"])[keep], np.asarray(d["z"], np.float32)[keep],
                         float(d["mean_cosine"])))
        data[cfg.dataset.corpus] = (cfg, recs)

    t = base.tuning
    grid = list(itertools.product(t.min_cluster_share, t.merge_threshold, t.single_speaker_threshold))
    rows = []
    for share, merge, single in grid:
        row = {"min_cluster_share": share, "merge_threshold": _fmt(merge), "single_speaker_threshold": _fmt(single)}
        terms, maes = [], []
        for corpus, (cfg, recs) in data.items():
            kt, kp = [], []
            for k_true, lab, z, mc in recs:
                out, _ = postprocess(lab, z, mc, share, merge, single)
                kt.append(k_true)
                kp.append(int(np.unique(out).size))
            m = count_metrics(kt, kp, cfg.evaluation.rel_error_tol)
            tag = "ami" if corpus == "ami" else "vox"
            for k in ("exact", "within1", "mae", "signed", "rel_acc"):
                row[f"{tag}_{k}"] = m[k]
            terms.append(m["exact"] if corpus == "ami" else m["rel_acc"])
            maes.append(m["mae"])
        row["objective"] = float(np.mean(terms))   # 0.5/0.5 when both sets exist
        row["mean_mae"] = float(np.mean(maes))
        rows.append(row)
    df = pd.DataFrame(rows)
    out_dir = ROOT / "results" / "tuning"
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / f"{method}.csv", index=False)
    # best: max objective, then min MAE, then the earliest (simplest) grid point
    df["_order"] = np.arange(len(df))
    best = df.sort_values(["objective", "mean_mae", "_order"], ascending=[False, True, True]).iloc[0]
    none = df.iloc[0]  # grid point 0 = no post-processing
    as_val = lambda v: None if v == "off" else float(v)  # noqa: E731
    result = {
        "min_cluster_share": float(best.min_cluster_share),
        "merge_threshold": as_val(best.merge_threshold),
        "single_speaker_threshold": as_val(best.single_speaker_threshold),
        "objective": float(best.objective),
        "objective_without_postprocessing": float(none.objective),
        "mean_mae": float(best.mean_mae),
        "mean_mae_without_postprocessing": float(none.mean_mae),
        "val_sets": vals,
        "objective_definition": "mean over available val sets of [exact (AMI dev) | rel_acc (Vox val)]",
        "git_commit": git_commit(),
    }
    dump_yaml(result, out_dir / method / "best.yaml")
    print(df.drop(columns="_order").sort_values(["objective", "mean_mae"], ascending=[False, True]).head(8).to_string(index=False))
    print(f"[tune {method}] best: {yaml.safe_dump({k: result[k] for k in list(result)[:7]}, sort_keys=False)}")
    return result
