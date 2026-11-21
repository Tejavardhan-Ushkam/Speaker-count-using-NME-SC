"""Print all headline result tables from saved predictions (no clustering is re-run).

    /home/pm_students/miniconda3/envs/spectral/bin/python scripts/show_results.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] / "results"
pd.set_option("display.width", 200)

METHODS = ["baseline_mode", "nmesc_ecapa", "nmesc_ecapa_pp", "nmesc_affnet", "nmesc_affnet_pp",
           "snet_affnet_pp", "snet_ecapa_pp"]
RUNS = {  # title -> (split dir, tag dir, methods)
    "AMI test (16 meetings, oracle VAD)": ("ami/test", "", METHODS),
    "AMI test, pyannote VAD": ("ami/test_pyannote", "", ["nmesc_ecapa", "snet_affnet_pp"]),
    "VoxConverse test (232 recordings, AMI-trained models)": ("voxconverse/test", "ami_trained", METHODS),
    "VoxConverse test, pyannote VAD (AMI-trained)": ("voxconverse/test_pyannote", "ami_trained",
                                                     ["nmesc_ecapa", "snet_affnet_pp"]),
    "VoxConverse test, pruning + p_min tuned on AMI dev + Vox val (tag vox_tuned)": (
        "voxconverse/test", "vox_tuned", ["nmesc_ecapa_pp", "snet_ecapa_pp"]),
    "VoxConverse test, mode baseline from Vox train (always 2)": ("voxconverse/test", "vox_trained", ["baseline_mode"]),
    "VoxConverse test, snet_ecapa_pp + SpectralNet warm start pre-trained on Vox train (tag vox_warm)": (
        "voxconverse/test", "vox_warm", ["snet_ecapa_pp"]),
    "AMI test, snet_ecapa_pp + warm start, Vox-tuned (tag vox_warm)": ("ami/test", "vox_warm", ["snet_ecapa_pp"]),
    "AMI test, pruning + p_min tuned on AMI dev + Vox val (tag vox_tuned)": (
        "ami/test", "vox_tuned", ["nmesc_ecapa_pp", "snet_ecapa_pp"]),
}


def load(split, tag, m):
    p = ROOT / split / m / tag / "predictions.csv" if tag else ROOT / split / m / "predictions.csv"
    return pd.read_csv(p) if p.exists() else None


def metrics(d, k="k_pred"):
    e = d[k] - d.k_true
    out = {"n": len(d), "exact": np.mean(e == 0), "±1": np.mean(e.abs() <= 1), "MAE": e.abs().mean(),
           "signed": e.mean(), "rel.acc": np.mean(e.abs() / d.k_true <= 0.15)}
    out["DER"] = d.der.mean() if "der" in d and d.der.notna().any() else np.nan
    return out


def title(t):
    print(f"\n{'=' * 100}\n{t}\n{'=' * 100}")


for name, (split, tag, ms) in RUNS.items():
    rows = {m: metrics(d) for m in ms if (d := load(split, tag, m)) is not None}
    if rows:
        title(name)
        print(pd.DataFrame(rows).T.round(3).to_string())

title("Post-processing: before (eigengap K) -> after (pruned/merged K)")
for split, tag, corpus in [("ami/test", "", "AMI"), ("voxconverse/test", "ami_trained", "VoxConverse")]:
    for m in ["nmesc_ecapa_pp", "snet_ecapa_pp", "nmesc_affnet_pp", "snet_affnet_pp"]:
        d = load(split, tag, m)
        if d is None:
            continue
        a, b = metrics(d, "k_eigengap"), metrics(d)
        pre, post = (d.k_eigengap - d.k_true).abs(), (d.k_pred - d.k_true).abs()
        print(f"{corpus:12s} {m:16s} exact {a['exact']:.3f} -> {b['exact']:.3f} | MAE {a['MAE']:.2f} -> {b['MAE']:.2f}"
              f" | signed {a['signed']:+.2f} -> {b['signed']:+.2f} | fixed {((pre > 0) & (post == 0)).sum():3d}"
              f" broken {((pre == 0) & (post > 0)).sum():3d}")


def kbin(k):
    return "1" if k == 1 else "2" if k == 2 else "3-4" if k <= 4 else "5-7" if k <= 7 else "8-12" if k <= 12 else "13+"


title("VoxConverse: MAE by true K bin (AMI-trained)")
order = ["1", "2", "3-4", "5-7", "8-12", "13+"]
tab = {}
for m in METHODS:
    d = load("voxconverse/test", "ami_trained", m)
    if d is None:
        continue
    d["bin"] = d.k_true.map(kbin)
    g = (d.k_pred - d.k_true).abs().groupby(d.bin).mean()
    if m == "nmesc_ecapa_pp":
        tab["(pp: before)"] = (d.k_eigengap - d.k_true).abs().groupby(d.bin).mean()
    tab[m] = g
    n = d.bin.value_counts()
print(pd.DataFrame(tab).T.reindex(columns=order).round(2).to_string())
print("n per bin:", {b: int(n.get(b, 0)) for b in order})

d = load("voxconverse/test", "ami_trained", "nmesc_ecapa")
if d is not None:
    s = d.n_segments <= 90
    e = (d.k_pred - d.k_true).abs()
    print(f"\nShort recordings (<=90 segments): n={s.sum()}, MAE {e[s].mean():.2f}; others: MAE {e[~s].mean():.2f}")

title("SpectralNet vs exact backend (K agreement)")
for split, tag in [("ami/dev", ""), ("ami/test", ""), ("voxconverse/test", "ami_trained")]:
    for m in ["snet_affnet_pp", "snet_ecapa_pp"]:
        d = load(split, tag, m)
        if d is not None and "snet_exact_agree" in d:
            print(f"{split:18s} {m:16s} agreement {d.snet_exact_agree.mean():.3f} ({int(d.snet_exact_agree.sum())}/{len(d)})")

print(f"\nFull tables, significance tests and inferences: {ROOT / 'SUMMARY.md'}")
