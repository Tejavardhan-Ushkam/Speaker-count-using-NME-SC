"""Phase 9 report (scope 1-6 speakers) from saved predictions -> results/scope6/summary.md (also printed).

    /home/pm_students/miniconda3/envs/spectral/bin/python scripts/scope6_report.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from speakercount.eval.stats import bootstrap_ci, paired_compare  # noqa: E402

R = ROOT / "results"
K6 = set((ROOT / "splits/voxconverse_test_k6.txt").read_text().split())


def load(split, m, tag, subset=None):
    p = R / split / m / tag / "predictions.csv" if tag else R / split / m / "predictions.csv"
    if not p.exists():
        return None
    d = pd.read_csv(p).set_index("recording_id")
    return d.loc[sorted(set(d.index) & subset)] if subset else d


def md(df, fmt=".3f"):
    """DataFrame -> markdown table (no tabulate dependency)."""
    f = lambda v: format(v, fmt) if isinstance(v, (float, np.floating)) else str(v)  # noqa: E731
    lines = ["| | " + " | ".join(map(str, df.columns)) + " |", "|---" * (len(df.columns) + 1) + "|"]
    lines += ["| " + str(i) + " | " + " | ".join(f(v) for v in r) + " |" for i, r in zip(df.index, df.values)]
    return "\n".join(lines)


def row(d, k="k_pred"):
    e = d[k] - d.k_true
    lo, hi = bootstrap_ci((e == 0).astype(float).values)
    return {"n": len(d), "exact": (e == 0).mean(), "exact 95% CI": f"[{lo:.2f}, {hi:.2f}]", "±1": (e.abs() <= 1).mean(),
            "MAE": e.abs().mean(), "signed": e.mean(),
            "DER": d.der.mean() if "der" in d and d.der.notna().any() else np.nan}


VOX = {  # name -> (split, method, tag, subset)
    "always 2 (mode of Vox train 1-6)": ("voxconverse/test", "baseline_mode", "scope6", None),
    "nmesc_ecapa (k_max 25)": ("voxconverse/test", "nmesc_ecapa", "ami_trained", K6),
    "nmesc_ecapa (k_max 6)": ("voxconverse/test", "nmesc_ecapa", "scope6", None),
    "snet_ecapa_pp, report-1 model": ("voxconverse/test", "snet_ecapa_pp", "vox_tuned", K6),
    "nmesc_ecapa_pp, scope-6 tuned (ablation)": ("voxconverse/test", "nmesc_ecapa_pp", "scope6", None),
    "**snet_ecapa_pp, scope-6 tuned**": ("voxconverse/test", "snet_ecapa_pp", "scope6", None),
}
AMI = {
    "always 4 (mode of AMI train)": ("ami/test", "baseline_mode", "", None),
    "nmesc_ecapa (k_max 10)": ("ami/test", "nmesc_ecapa", "", None),
    "nmesc_ecapa (k_max 6)": ("ami/test", "nmesc_ecapa", "scope6", None),
    "snet_ecapa_pp, report-1 model": ("ami/test", "snet_ecapa_pp", "vox_tuned", None),
    "nmesc_ecapa_pp, scope-6 tuned (ablation)": ("ami/test", "nmesc_ecapa_pp", "scope6", None),
    "**snet_ecapa_pp, scope-6 tuned**": ("ami/test", "snet_ecapa_pp", "scope6", None),
}
out = ["# Phase 9: scope 1-6 speakers (VoxConverse test 1-6: 117 recordings; AMI test: 16)\n"]
for tf in ("snet_ecapa_pp", "nmesc_ecapa_pp"):
    f = R / "tuning_k6" / tf / "best.yaml"
    if f.exists():
        b = yaml.safe_load(f.read_text())
        out.append(f"Tuned on val ({tf}): k_max {b['k_max']}, p_min {b['p_min']}, pruning {b['share_mode']} "
                   f"{b['min_cluster_share']}, merge {b['merge_threshold']}, single {b['single_speaker_threshold']}; "
                   f"val worst-corpus exact {b['objective']:.3f} (no post-processing {b['objective_without_postprocessing']:.3f})")
        t = pd.read_csv(R / "tuning_k6" / f"{tf}.csv")
        m = t[(t.k_max.astype(str) == str(b["k_max"])) & (t.p_min == b["p_min"]) & (t.share_mode == b["share_mode"])
              & (t.min_cluster_share == b["min_cluster_share"])
              & (t.merge_threshold.astype(str) == str(b["merge_threshold"] if b["merge_threshold"] is not None else "off"))
              & (t.single_speaker_threshold.astype(str) == str(b["single_speaker_threshold"] if b["single_speaker_threshold"] is not None else "off"))]
        if len(m):
            m = m.iloc[0]
            out.append(f"  val detail: AMI (dev+train, n={int(m.ami_n)}) exact {m.ami_exact:.3f}; "
                       f"Vox (train+val 1-6, n={int(m.vox_n)}) exact {m.vox_exact:.3f}\n")
ref = {"vox": load("voxconverse/test", "nmesc_ecapa", "scope6"), "ami": load("ami/test", "nmesc_ecapa", "scope6")}
for title, runs, key in (("VoxConverse test, 1-6 speakers", VOX, "vox"), ("AMI test", AMI, "ami")):
    rows, tests = {}, []
    for name, (split, m, tag, sub) in runs.items():
        d = load(split, m, tag, sub)
        if d is None:
            continue
        rows[name] = row(d)
        r = ref[key]
        if r is not None and "nmesc_ecapa (k_max" not in name and "always" not in name:
            j = d.index.intersection(r.index)
            c = paired_compare(d.k_true[j], d.k_pred[j], r.k_pred[j])
            tests.append(f"| {name} | {c['d_exact']:+.3f} [{c['d_exact_ci'][0]:+.3f}, {c['d_exact_ci'][1]:+.3f}] | "
                         f"{c['d_mae']:+.3f} [{c['d_mae_ci'][0]:+.3f}, {c['d_mae_ci'][1]:+.3f}] | {c['wilcoxon_p']:.2g} |")
    if rows:
        out += [f"## {title}\n", md(pd.DataFrame(rows).T), ""]
        if tests:
            out += ["Paired vs nmesc_ecapa (k_max 6), 10k bootstrap:\n", "| method | Δexact [95% CI] | ΔMAE [95% CI] | Wilcoxon p |",
                    "|---|---|---|---|", *tests, ""]
# cumulative ranges on VoxConverse 1-6
RANGES = [("1", 1, 1), ("1-2", 1, 2), ("1-4", 1, 4), ("1-6", 1, 6), ("3-6", 3, 6), ("4-6", 4, 6)]
tab = {}
for name, (split, m, tag, sub) in VOX.items():
    d = load(split, m, tag, sub)
    if d is None or "always" in name:
        continue
    tab[name] = {r: ((s := d[(d.k_true >= lo) & (d.k_true <= hi)]).k_pred == s.k_true).mean() for r, lo, hi in RANGES}
if tab:
    d = load("voxconverse/test", "nmesc_ecapa", "ami_trained", K6)
    n = {r: int(((d.k_true >= lo) & (d.k_true <= hi)).sum()) for r, lo, hi in RANGES}
    out += ["## VoxConverse test: exact accuracy by true-K range\n", f"recordings per range: {n}\n",
            md(pd.DataFrame(tab).T, ".2f"), ""]
d = load("voxconverse/test", "snet_ecapa_pp", "scope6_all")
if d is not None:
    out += ["## VoxConverse test, all 232 recordings (the K cap cannot reach K > cap; context only)\n",
            md(pd.DataFrame({"snet_ecapa_pp, scope-6 tuned": row(d)}).T), ""]
txt = "\n".join(out)
(R / "scope6").mkdir(exist_ok=True)
(R / "scope6" / "summary.md").write_text(txt + "\n")
print(txt)
