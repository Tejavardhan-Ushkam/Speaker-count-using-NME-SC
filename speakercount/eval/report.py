"""Per-run summary.md (prompt §6.1)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from ..config import ROOT, Cfg, git_commit, results_dir
from .metrics import cluster_health, confusion, count_metrics, per_bin
from .stats import bootstrap_ci, paired_compare

BASELINES = ("baseline_mode", "nmesc_ecapa")


def _f(x, nd=4):
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return "–"
    return f"{x:.{nd}f}" if isinstance(x, (float, np.floating)) else str(x)


def md_table(df: pd.DataFrame, floatfmt: int = 3) -> str:
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(_f(v, floatfmt) if isinstance(v, (float, np.floating)) else str(v)
                                       for v in r.values) + " |")
    return "\n".join(lines)


def load_predictions(corpus: str, split: str, method: str, tag: str = "") -> pd.DataFrame | None:
    p = ROOT / "results" / corpus / split / method
    if tag:
        p = p / tag
    f = p / "predictions.csv"
    return pd.read_csv(f) if f.exists() else None


def write_report(cfg: Cfg) -> Path:
    out = results_dir(cfg)
    df = pd.read_csv(out / "predictions.csv")
    tau = cfg.evaluation.rel_error_tol
    k_max = cfg.clustering.k_max
    m = count_metrics(df.k_true, df.k_pred, tau)
    name = cfg.method.name + (f" [{cfg.method.tag}]" if cfg.method.tag else "")
    L = [f"# {name} — {cfg.dataset.corpus} / {cfg.dataset.split}", ""]
    L += [f"git commit `{git_commit()}`; resolved config in `config_resolved.yaml`.", ""]

    pp_file = out / "postprocess_used.yaml"
    pp = yaml.safe_load(pp_file.read_text()) if pp_file.exists() else {}
    L += ["## Configuration", "", "| key | value |", "|---|---|"]
    items = [("affinity.source", cfg.affinity.source), ("clustering.backend", cfg.clustering.backend),
             ("clustering.laplacian", cfg.clustering.laplacian), ("clustering.k_max", k_max),
             ("clustering.p_max_abs", cfg.clustering.p_max_abs),
             ("clustering.coarse_to_fine", cfg.clustering.coarse_to_fine),
             ("clustering.eig_solver", cfg.clustering.eig_solver), ("vad.source", cfg.vad.source),
             ("affinity.refine", cfg.affinity.refine),
             ("affinity.oracle_overlap_removal (ORACLE)", cfg.affinity.oracle_overlap_removal),
             ("postprocess.enabled", cfg.postprocess.enabled)]
    if cfg.postprocess.enabled:
        items += [(f"postprocess.{k} (used)", v) for k, v in pp.items()]
    for k, v in items:
        L.append(f"| {k} | {v} |")
    L += [""]

    L += ["## Counting accuracy", "",
          "| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=%.2f) | mean rel. err | median rel. err |" % tau,
          "|---|---|---|---|---|---|---|---|",
          f"| {m['n']} | {m['exact']:.4f} | {m['within1']:.4f} | {m['mae']:.4f} | {m['signed']:+.3f} | "
          f"{m['rel_acc']:.4f} | {m['rel_err_mean']:.4f} | {m['rel_err_median']:.4f} |", ""]
    abs_err = (df.k_pred - df.k_true).abs()
    lo, hi = bootstrap_ci(abs_err.values, cfg.evaluation.bootstrap)
    lo2, hi2 = bootstrap_ci((abs_err == 0).astype(float).values, cfg.evaluation.bootstrap)
    L += [f"Bootstrap 95 % CI: MAE [{lo:.3f}, {hi:.3f}], exact [{lo2:.3f}, {hi2:.3f}].", ""]

    L += ["## Per-K-bin breakdown", "", md_table(per_bin(df, tau)), ""]
    L += ["## Confusion (rows K, columns K^)", "", md_table(confusion(df).reset_index()), ""]

    if df["der"].notna().any():
        L += ["## DER (collar ±0.25 s)", "",
              "| | mean DER | miss | FA | confusion | DER, overlap skipped |", "|---|---|---|---|---|---|",
              f"| {name} | {df.der.mean():.4f} | {df.get('der_miss', pd.Series([np.nan])).mean():.4f} | "
              f"{df.get('der_fa', pd.Series([np.nan])).mean():.4f} | {df.get('der_conf', pd.Series([np.nan])).mean():.4f} | "
              f"{df.der_no_overlap.mean():.4f} |", ""]
        if cfg.vad.source == "oracle":
            L += ["With oracle VAD the missed-speech part of DER comes only from overlapped speech "
                  "(one label per frame), and false alarm is ~0.", ""]

        h = cluster_health(df, k_max)
        L += ["## Cluster health (number of recordings)", "", "| " + " | ".join(h) + " |",
              "|" + "---|" * len(h), "| " + " | ".join(str(v) for v in h.values()) + " |", ""]

        L += ["## p* distribution", ""]
        ps = df.p_star[df.p_star > 0]
        pmax = cfg.clustering.p_max_abs
        hits = int((ps >= pmax).sum()) if pmax is not None else 0
        L += [f"median {ps.median():.0f}, max {ps.max():.0f}, hits p_max_abs={pmax}: {hits}/{len(ps)}"
              + ("  **(often at the cap: raise p_max_abs)**" if len(ps) and hits / len(ps) > 0.2 else ""), ""]

        L += ["## Timing", "", f"clustering total {df.cluster_sec.sum() / 60:.2f} min "
              f"({df.cluster_sec.sum():.1f} s, {df.cluster_sec.mean():.2f} s/recording, max {df.cluster_sec.max():.1f} s)", ""]

        if "snet_exact_agree" in df and df.snet_exact_agree.notna().any() and cfg.clustering.backend == "spectralnet":
            agree = pd.to_numeric(df.snet_exact_agree, errors="coerce")
            rel = pd.to_numeric(df.get("snet_ritz_max_relerr"), errors="coerce")
            rate = agree.mean()
            L += ["## SpectralNet v2 self-check", "",
                  f"K^ agreement with exact eigh: **{rate:.3f}** ({int(agree.sum())}/{agree.notna().sum()}); "
                  f"Ritz-value max rel. error: median {rel.median():.2e}, max {rel.max():.2e}."
                  + ("  **WARNING: agreement < 90 %**" if rate < 0.9 else ""), ""]

    # comparison against baselines
    comp = []
    for b in BASELINES:
        if b == cfg.method.name and not cfg.method.tag:
            continue
        bdf = load_predictions(cfg.dataset.corpus, cfg.dataset.split, b)
        if bdf is None:
            continue
        j = df.merge(bdf[["recording_id", "k_pred"]], on="recording_id", suffixes=("", "_b"))
        pc = paired_compare(j.k_true, j.k_pred, j.k_pred_b, cfg.evaluation.bootstrap)
        bm = count_metrics(j.k_true, j.k_pred_b, tau)
        comp.append(f"| {b} | {bm['exact']:.4f} | {bm['mae']:.4f} | {pc['d_exact']:+.3f} "
                    f"[{pc['d_exact_ci'][0]:+.3f}, {pc['d_exact_ci'][1]:+.3f}] | {pc['d_mae']:+.3f} "
                    f"[{pc['d_mae_ci'][0]:+.3f}, {pc['d_mae_ci'][1]:+.3f}] | {pc['wilcoxon_p']:.3g} |")
    if comp:
        L += ["## Against the baselines (paired; differences = this run − baseline)", "",
              "| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |",
              "|---|---|---|---|---|---|"] + comp
        if len(df) < 30:
            L += ["", f"n = {len(df)} recordings: statistical power is low."]
        L += [""]

    # worst recordings
    df2 = df.assign(abs_err=abs_err).sort_values(["abs_err", "recording_id"], ascending=[False, True]).head(5)
    L += ["## 5 worst recordings", "", "| rec | K | K^ | cluster sizes % | gap_ratio | p* |", "|---|---|---|---|---|---|"]
    for _, r in df2.iterrows():
        sizes = "–"
        f = out / "recs" / f"{r.recording_id}.npz"
        if f.exists():
            with np.load(f) as d:
                if "cluster_sizes" in d.files:
                    sizes = " ".join(f"{100 * s:.0f}" for s in d["cluster_sizes"])
        L.append(f"| {r.recording_id} | {r.k_true} | {r.k_pred} | {sizes} | {_f(r.gap_ratio, 2)} | {r.p_star} |")
    L += [""]

    L += ["## Per-recording predictions", "", "See `predictions.csv`.", ""]
    (out / "summary.md").write_text("\n".join(L))
    print(f"[report] wrote {out / 'summary.md'}")
    return out / "summary.md"
