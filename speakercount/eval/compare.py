"""`compare`: cross-method results/SUMMARY.md (prompt §6.2).

Tables are generated from predictions.csv files; the hand-written inferences, failure analysis
and next steps live in results/inferences.md and are appended verbatim (they must be written
from the numbers, not boilerplate).
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd
import yaml

from ..config import ROOT, git_commit
from .metrics import count_metrics
from .stats import paired_compare

METHODS = ["baseline_mode", "nmesc_ecapa", "nmesc_ecapa_pp", "nmesc_affnet", "nmesc_affnet_pp",
           "snet_affnet_pp", "snet_ecapa_pp"]
HEADLINE = [("ami", "test", "AMI test"), ("voxconverse", "test", "VoxConverse test")]
VAL = [("ami", "dev", "AMI dev"), ("voxconverse", "val", "VoxConverse val")]
COLS = [("exact", True), ("within1", True), ("mae", False), ("signed", None), ("rel_acc", True), ("der", False)]


def _load(corpus, split, method, tag=""):
    p = ROOT / "results" / corpus / split / method
    if tag:
        p = p / tag
    f = p / "predictions.csv"
    return pd.read_csv(f) if f.exists() else None


def _metrics(df):
    m = count_metrics(df.k_true, df.k_pred)
    m["der"] = float(df.der.mean()) if "der" in df and df.der.notna().any() else float("nan")
    m["der_no_overlap"] = float(df.der_no_overlap.mean()) if "der_no_overlap" in df and df.der_no_overlap.notna().any() else float("nan")
    return m


def _table(rows: dict[str, dict], extra_cols=()) -> list[str]:
    best = {}
    for c, hi in COLS:
        vals = [r[c] for r in rows.values() if np.isfinite(r.get(c, np.nan))]
        if not vals or hi is None:
            continue
        best[c] = max(vals) if hi else min(vals)
    names = {"exact": "exact", "within1": "±1", "mae": "MAE", "signed": "signed err", "rel_acc": "rel. acc", "der": "DER"}
    head = "| method | n | " + " | ".join(names[c] for c, _ in COLS) + "".join(f" | {e}" for e in extra_cols) + " |"
    out = [head, "|" + "---|" * (2 + len(COLS) + len(extra_cols))]
    for m, r in rows.items():
        cells = []
        for c, _ in COLS:
            v = r.get(c, np.nan)
            if not np.isfinite(v):
                cells.append("–")
                continue
            s = f"{v:+.3f}" if c == "signed" else f"{v:.3f}"
            cells.append(f"**{s}**" if c in best and abs(v - best[c]) < 1e-12 else s)
        out.append(f"| {m} | {r['n']} | " + " | ".join(cells) + "".join(f" | {r.get(e, '')}" for e in extra_cols) + " |")
    return out


def _identical_warnings(corpus, split, methods) -> list[str]:
    dfs = {m: _load(corpus, split, m) for m in methods}
    dfs = {m: d.set_index("recording_id").k_pred for m, d in dfs.items() if d is not None}
    w = []
    for a, b in itertools.combinations(dfs, 2):
        if {a, b} == {"nmesc_ecapa", "baseline_mode"}:
            pass
        j = pd.concat([dfs[a], dfs[b]], axis=1, join="inner")
        if len(j) and (j.iloc[:, 0] == j.iloc[:, 1]).all():
            w.append(f"- **WARNING** {corpus}/{split}: `{a}` and `{b}` give identical K^ on all {len(j)} recordings.")
    return w


ABLATIONS = [  # (ablation, label, method, tag, split suffix)
    ("Laplacian", "unnormalized (default)", "nmesc_ecapa", "", ""),
    ("Laplacian", "sym_norm", "nmesc_ecapa", "lap_symnorm", ""),
    ("Laplacian", "unnormalized (default), AffinityNet", "nmesc_affnet", "", ""),
    ("Laplacian", "sym_norm, AffinityNet", "nmesc_affnet", "lap_symnorm", ""),
    ("AffinityNet context", "4-layer Transformer (default)", "nmesc_affnet", "", ""),
    ("AffinityNet context", "0 layers (per-segment residual MLP)", "nmesc_affnet", "ctx0", ""),
    ("Time encoding", "on (default)", "nmesc_affnet", "", ""),
    ("Time encoding", "off", "nmesc_affnet", "no_time", ""),
    ("Speaker-dropout augmentation", "on (default)", "nmesc_affnet", "", ""),
    ("Speaker-dropout augmentation", "off", "nmesc_affnet", "no_spkdrop", ""),
    ("Loss", "BCE + SupCon (default)", "nmesc_affnet", "", ""),
    ("Loss", "BCE only", "nmesc_affnet", "bce_only", ""),
    ("Overlap handling (training labels)", "clean-only loss (default)", "nmesc_affnet", "", ""),
    ("Overlap handling (training labels)", "most-overlap labels (old project)", "nmesc_affnet", "most_overlap", ""),
    ("Oracle overlap removal (ORACLE, upper bound)", "off, raw ECAPA", "nmesc_ecapa", "", ""),
    ("Oracle overlap removal (ORACLE, upper bound)", "on, raw ECAPA", "nmesc_ecapa", "oracle_overlap_removal", ""),
    ("Oracle overlap removal (ORACLE, upper bound)", "off, AffinityNet", "nmesc_affnet", "", ""),
    ("Oracle overlap removal (ORACLE, upper bound)", "on, AffinityNet", "nmesc_affnet", "oracle_overlap_removal", ""),
    ("Refinement ops (Wang et al. 2018)", "off, raw ECAPA", "nmesc_ecapa", "", ""),
    ("Refinement ops (Wang et al. 2018)", "on, raw ECAPA", "nmesc_ecapa", "refine", ""),
    ("Refinement ops (Wang et al. 2018)", "off, AffinityNet", "nmesc_affnet", "", ""),
    ("Refinement ops (Wang et al. 2018)", "on, AffinityNet", "nmesc_affnet", "refine", ""),
    ("SpectralNet warm start", "on (default)", "snet_affnet_pp", "", ""),
    ("SpectralNet warm start", "off", "snet_affnet_pp", "no_warm", ""),
    ("VAD", "oracle, nmesc_ecapa", "nmesc_ecapa", "", ""),
    ("VAD", "pyannote, nmesc_ecapa", "nmesc_ecapa", "", "_pyannote"),
    ("VAD", "oracle, snet_affnet_pp", "snet_affnet_pp", "", ""),
    ("VAD", "pyannote, snet_affnet_pp", "snet_affnet_pp", "", "_pyannote"),
    ("Old Siamese, flaws 1-2 fixed only", "raw ECAPA (nmesc_ecapa)", "nmesc_ecapa", "", ""),
    ("Old Siamese, flaws 1-2 fixed only", "Siamese (no output ReLU, cosine loss)", "nmesc_affnet", "siamese_fixed", ""),
    ("Old Siamese, flaws 1-2 fixed only", "AffinityNet (nmesc_affnet)", "nmesc_affnet", "", ""),
]


def ablation_table(corpus: str = "ami") -> list[str]:
    def cell(split, method, tag):
        d = _load(corpus, split, method, tag)
        if d is None:
            return ["–"] * 3
        m = _metrics(d)
        return [f"{m['exact']:.3f}", f"{m['mae']:.3f}", "–" if not np.isfinite(m["der"]) else f"{m['der']:.3f}"]

    L = [f"AMI only (VoxConverse unavailable, so the \"training corpora\" ablation is not run). Each variant "
         "differs from its default in one setting; AffinityNet variants were retrained and selected on AMI dev "
         "exactly like the default. No post-processing in these rows unless the method name says `_pp`.", "",
         "| ablation | variant | dev exact | dev MAE | test exact | test MAE | test DER |", "|---|---|---|---|---|---|---|"]
    last = None
    for abl, label, method, tag, suf in ABLATIONS:
        dev = cell("dev" + suf, method, tag) if not suf else ["–"] * 3
        test = cell("test" + suf, method, tag)
        if test[0] == "–" and dev[0] == "–":
            continue
        L.append(f"| {abl if abl != last else ''} | {label} | {dev[0]} | {dev[1]} | {test[0]} | {test[1]} | {test[2]} |")
        last = abl
    # warm start: fit time
    t = []
    for tag, name in (("", "on"), ("no_warm", "off")):
        d = _load(corpus, "test", "snet_affnet_pp", tag)
        if d is not None:
            t.append(f"{name}: {d.cluster_sec.mean():.1f} s/recording")
    if t:
        L += ["", "SpectralNet warm start, mean clustering time per AMI test recording — " + "; ".join(t) + "."]
    return L


def compare() -> None:
    (ROOT / "results" / "ablations.md").write_text("\n".join(ablation_table()) + "\n")
    L = ["# Speaker-count v2 — cross-method summary", "",
         f"git commit `{git_commit()}`. Generated by `python run.py compare`; inferences written by hand from these numbers.", ""]
    avail = [h for h in HEADLINE if any(_load(c, s, m) is not None for m in METHODS for c, s, _ in [h])]
    missing = [h[2] for h in HEADLINE if h not in avail]
    if missing:
        L += [f"> **Not available:** {', '.join(missing)} — VoxConverse data is not in `dataset/` yet; "
              "everything below is AMI-only (training, tuning and testing).", ""]

    L += ["## 1. Headline (test sets, oracle VAD)", ""]
    for corpus, split, title in avail:
        rows = {}
        for m in METHODS:
            d = _load(corpus, split, m)
            if d is not None:
                rows[m] = _metrics(d)
        L += [f"### {title}", ""] + _table(rows) + [""]
        ref = _load(corpus, split, "nmesc_ecapa")
        if ref is not None:
            L += [f"Paired vs `nmesc_ecapa` ({title}; Δ = method − nmesc_ecapa; 10 000 bootstrap resamples; Wilcoxon on |K^−K|):", "",
                  "| method | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p |", "|---|---|---|---|"]
            for m in METHODS:
                d = _load(corpus, split, m)
                if d is None or m == "nmesc_ecapa":
                    continue
                j = d.merge(ref[["recording_id", "k_pred"]], on="recording_id", suffixes=("", "_ref"))
                pc = paired_compare(j.k_true, j.k_pred, j.k_pred_ref)
                L.append(f"| {m} | {pc['d_exact']:+.3f} [{pc['d_exact_ci'][0]:+.3f}, {pc['d_exact_ci'][1]:+.3f}] | "
                         f"{pc['d_mae']:+.3f} [{pc['d_mae_ci'][0]:+.3f}, {pc['d_mae_ci'][1]:+.3f}] | {pc['wilcoxon_p']:.3g} |")
            L += [""]
        # per-recording K^
        kp = {m: _load(corpus, split, m) for m in METHODS}
        kp = {m: d.set_index("recording_id").k_pred for m, d in kp.items() if d is not None}
        if kp:
            tab = pd.DataFrame(kp)
            first = next(d for d in (_load(corpus, split, m) for m in METHODS) if d is not None)
            tab.insert(0, "K", first.set_index("recording_id").k_true)
            if len(tab) <= 40:
                L += [f"Per-recording K^ ({title}):", "", "| rec | " + " | ".join(tab.columns) + " |",
                      "|" + "---|" * (len(tab.columns) + 1)]
                for rec, r in tab.iterrows():
                    L.append(f"| {rec} | " + " | ".join(str(int(v)) if pd.notna(v) else "–" for v in r.values) + " |")
                L += [""]
        # pyannote VAD
        vrows = {}
        for m in METHODS:
            d = _load(corpus, f"{split}_pyannote", m)
            if d is not None:
                vrows[m + " (pyannote VAD)"] = _metrics(d)
        if vrows:
            L += [f"Realistic VAD (pyannote/segmentation-3.0), {title}:", ""] + _table(vrows) + [""]

    L += ["## 2. Validation sets (all tuning and model selection used only these)", ""]
    for corpus, split, title in VAL:
        rows = {}
        for m in METHODS:
            d = _load(corpus, split, m)
            if d is not None:
                r = _metrics(d)
                bf = ROOT / "results" / "tuning" / m / "best.yaml"
                if bf.exists():
                    b = yaml.safe_load(bf.read_text())
                    r["tuned"] = (f"share {b['min_cluster_share']}, merge {b['merge_threshold'] or 'off'}, "
                                  f"single {b['single_speaker_threshold'] or 'off'}")
                rows[m] = r
        if rows:
            L += [f"### {title}", ""] + _table(rows, extra_cols=("tuned",)) + [""]
        else:
            L += [f"### {title}", "", "Not available.", ""]

    abl = ROOT / "results" / "ablations.md"
    L += ["## 3. Ablations", ""]
    L += [abl.read_text().strip(), ""] if abl.exists() else ["Not run yet.", ""]

    warn = []
    for corpus, split, _ in avail + VAL:
        warn += _identical_warnings(corpus, split, [m for m in METHODS if m != "baseline_mode"])
    L += ["## Silent no-op check", ""] + (warn or ["No two methods produced identical K^ on every recording of a split."]) + [""]

    inf = ROOT / "results" / "inferences.md"
    L += [inf.read_text().strip(), ""] if inf.exists() else ["## 4. Inferences", "", "_to be written_", ""]
    plots = ROOT / "results" / "plots" / "captions.md"
    if plots.exists():
        L += [plots.read_text().strip(), ""]
    out = ROOT / "results" / "SUMMARY.md"
    out.write_text("\n".join(L) + "\n")
    print(f"[compare] wrote {out}")
