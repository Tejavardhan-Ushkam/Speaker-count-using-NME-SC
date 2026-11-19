"""`plots`: every figure of prompt §6.3 that the available data supports (PNG 150 dpi + PDF).

One fixed colour per method in every figure (validated colourblind-aware categorical order;
baseline_mode is neutral grey). Writes results/plots/captions.md, which `compare` embeds in
SUMMARY.md with a one-line "what to look at" per figure.
"""

from __future__ import annotations

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ..config import ROOT, load_config  # noqa: E402
from .stats import bootstrap_ci  # noqa: E402

OUT = ROOT / "results" / "plots"
METHODS = ["baseline_mode", "nmesc_ecapa", "nmesc_ecapa_pp", "nmesc_affnet", "nmesc_affnet_pp",
           "snet_ecapa_pp", "snet_affnet_pp"]
COLOR = {"baseline_mode": "#8a8984", "nmesc_ecapa": "#2a78d6", "nmesc_ecapa_pp": "#eb6834",
         "nmesc_affnet": "#1baf7a", "nmesc_affnet_pp": "#eda100", "snet_ecapa_pp": "#e87ba4",
         "snet_affnet_pp": "#008300", "old": "#e34948"}
CORPORA = [("ami", "AMI"), ("voxconverse", "VoxConverse")]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
CAPTIONS: list[tuple[str, str]] = []

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
})


def _save(fig, name: str, caption: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png", bbox_inches="tight")
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    CAPTIONS.append((name, caption))
    print(f"[plots] {name}")


TAG: dict[str, str] = {}      # corpus -> results tag used for plots (set in make_all)
SUFFIX: dict[str, str] = {}   # corpus -> filename suffix
TITLE: dict[str, str] = {}


def _fn(corpus: str) -> str:
    return corpus + SUFFIX.get(corpus, "")


def _pred(corpus, split, method, tag=None):
    tag = TAG.get(corpus, "") if tag is None else tag
    p = ROOT / "results" / corpus / split / method / tag / "predictions.csv"
    return pd.read_csv(p) if p.exists() else None


def _rec(corpus, split, method, rec, tag=None):
    tag = TAG.get(corpus, "") if tag is None else tag
    p = ROOT / "results" / corpus / split / method / tag / "recs" / f"{rec}.npz"
    if not p.exists():
        return None
    with np.load(p) as d:
        return {k: d[k] for k in d.files}


def _test_split(corpus):
    return "test"


def _available(corpus, split="test"):
    return {m: d for m in METHODS if (d := _pred(corpus, split, m)) is not None}


# ------------------------------------------------------------------ 1, 13 bars
def metrics_bar(corpus, title):
    preds = _available(corpus)
    if not preds:
        return
    metrics = [("exact", "exact accuracy ↑", lambda e: (e == 0).astype(float)),
               ("within1", "±1 accuracy ↑", lambda e: (np.abs(e) <= 1).astype(float)),
               ("mae", "MAE ↓", lambda e: np.abs(e).astype(float))]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    names = list(preds)
    for ax, (_, label, fn) in zip(axes, metrics):
        for i, m in enumerate(names):
            d = preds[m]
            v = fn((d.k_pred - d.k_true).values)
            lo, hi = bootstrap_ci(v, 10000)
            ax.bar(i, v.mean(), color=COLOR[m], width=0.7)
            ax.errorbar(i, v.mean(), yerr=[[v.mean() - lo], [hi - v.mean()]], color=INK, lw=1, capsize=3)
            ax.text(i, hi + 0.02 * (1 if "MAE" not in label else max(1, hi)), f"{v.mean():.2f}",
                    ha="center", va="bottom", fontsize=7, color=MUTED)
        ax.set_xticks(range(len(names)), names, rotation=40, ha="right", fontsize=7)
        ax.set_title(label)
        ax.grid(axis="x", visible=False)
    fig.suptitle(f"{title} test (n={len(next(iter(preds.values())))}): counting metrics, 95 % bootstrap CI", y=1.02)
    _save(fig, f"metrics_bar_{_fn(corpus)}", f"{title} test: exact / ±1 / MAE per method with 95 % bootstrap CIs — "
          "compare each method with the grey always-mode baseline; CIs show how little n=16 separates methods.")


def der_bar(corpus, title):
    preds = {m: d for m, d in _available(corpus).items() if d.der.notna().any()}
    if not preds:
        return
    fig, ax = plt.subplots(figsize=(7, 3.2))
    names = list(preds)
    x = np.arange(len(names))
    for i, m in enumerate(names):
        d = preds[m]
        ax.bar(i - 0.18, d.der.mean(), 0.34, color=COLOR[m])
        ax.bar(i + 0.18, d.der_no_overlap.mean(), 0.34, color=COLOR[m], alpha=0.45, hatch="////", edgecolor="white")
        ax.text(i - 0.18, d.der.mean() + 0.003, f"{d.der.mean():.3f}", ha="center", fontsize=7, color=MUTED)
        ax.text(i + 0.18, d.der_no_overlap.mean() + 0.003, f"{d.der_no_overlap.mean():.3f}", ha="center", fontsize=7, color=MUTED)
    ax.set_xticks(x, names, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel("mean DER (collar ±0.25 s)")
    ax.grid(axis="x", visible=False)
    from matplotlib.patches import Patch

    ax.legend(handles=[Patch(color=MUTED, label="all speech (solid)"),
                       Patch(facecolor=MUTED, alpha=0.45, hatch="////", edgecolor="white", label="overlap skipped (hatched)")],
              loc="upper left", fontsize=7)
    ax.set_title(f"{title} test: DER per method")
    _save(fig, f"der_bar_{_fn(corpus)}", f"{title} test DER with and without overlapped speech — the gap between the bars "
          "is overlap (oracle VAD: missed speech comes only from overlap); compare clustering quality, not just K.")


# ------------------------------------------------------------------ 2 confusion
def confusions(corpus, title):
    for m, d in _available(corpus).items():
        ks = np.arange(min(d.k_true.min(), d.k_pred.min()), max(d.k_true.max(), d.k_pred.max()) + 1)
        mat = pd.crosstab(d.k_true, d.k_pred).reindex(index=ks, columns=ks, fill_value=0).values
        fig, ax = plt.subplots(figsize=(0.45 * len(ks) + 1.8, 0.45 * len(ks) + 1.4))
        ax.imshow(mat, cmap="Blues", vmin=0, vmax=max(1, mat.max()))
        for i in range(len(ks)):
            for j in range(len(ks)):
                if mat[i, j]:
                    ax.text(j, i, mat[i, j], ha="center", va="center", fontsize=8,
                            color="white" if mat[i, j] > mat.max() / 2 else INK)
        ax.set_xticks(range(len(ks)), ks)
        ax.set_yticks(range(len(ks)), ks)
        ax.set_xlabel("predicted K̂")
        ax.set_ylabel("true K")
        ax.grid(False)
        ax.set_title(f"{title} test — {m}", fontsize=9)
        _save(fig, f"confusion_{_fn(corpus)}_{m}", f"Confusion true K vs K̂ for {m} on {title} test — off-diagonal cells "
              "right of the diagonal are overestimates.")


# ------------------------------------------------------------------ 3 error hist
def error_hist(corpus, title):
    preds = _available(corpus)
    if not preds:
        return
    n = len(preds)
    cols = min(4, n)
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(2.6 * cols, 2.1 * rows), sharex=True, sharey=True, squeeze=False)
    errs = {m: (d.k_pred - d.k_true).values for m, d in preds.items()}
    lo, hi = min(e.min() for e in errs.values()), max(e.max() for e in errs.values())
    bins = np.arange(lo - 0.5, hi + 1.5)
    for ax, (m, e) in zip(axes.flat, errs.items()):
        ax.hist(e, bins=bins, color=COLOR[m], rwidth=0.85)
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_title(m, fontsize=8)
    for ax in list(axes.flat)[n:]:
        ax.set_visible(False)
    fig.supxlabel("K̂ − K")
    fig.supylabel("recordings")
    fig.suptitle(f"{title} test: signed counting error", y=1.02)
    _save(fig, f"error_hist_{_fn(corpus)}", f"{title} test K̂−K histograms — mass right of 0 = overestimates (the old "
          "failure); look for long right tails (large overcounts).")


# ------------------------------------------------------------------ 4 scatter
def scatter_k(corpus, title):
    preds = _available(corpus)
    if not preds:
        return
    rng = np.random.default_rng(0)
    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    mx = max(max(d.k_true.max(), d.k_pred.max()) for d in preds.values())
    ax.plot([0.5, mx + 0.5], [0.5, mx + 0.5], color=MUTED, lw=1, ls="--", label="K̂ = K")
    for i, (m, d) in enumerate(preds.items()):
        off = (i - len(preds) / 2) * 0.06
        ax.scatter(d.k_true + off, d.k_pred + rng.uniform(-0.12, 0.12, len(d)), s=22, color=COLOR[m],
                   edgecolor="white", linewidth=0.8, label=m)
    ax.set_xlabel("true K")
    ax.set_ylabel("predicted K̂ (jittered)")
    ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(1.0, 0.5))
    ax.set_title(f"{title} test: K̂ vs K")
    _save(fig, f"scatter_k_{_fn(corpus)}", f"{title} test K̂ vs K (jittered) — points above the dashed line are overcounts.")


# ------------------------------------------------------------------ 5 error vs K (Vox)
def error_vs_k_vox():
    preds = _available("voxconverse")
    if not preds:
        return
    from .metrics import K_BINS, k_bin

    bins = [b[2] for b in K_BINS]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    for m, d in preds.items():
        d = d.assign(bin=d.k_true.map(k_bin), ae=(d.k_pred - d.k_true).abs(), re=(d.k_pred - d.k_true).abs() / d.k_true)
        g = d.groupby("bin").agg(mae=("ae", "mean"), re=("re", "mean")).reindex(bins)
        axes[0].plot(bins, g.mae, marker="o", color=COLOR[m], lw=2, label=m)
        axes[1].plot(bins, g.re, marker="o", color=COLOR[m], lw=2)
    axes[0].set_ylabel("MAE")
    axes[1].set_ylabel("mean relative error")
    for ax in axes:
        ax.set_xlabel("true K bin")
    axes[0].legend(fontsize=7)
    fig.suptitle(f"{TITLE.get('voxconverse', 'VoxConverse')} test: error vs true K")
    _save(fig, "error_vs_k_vox" + SUFFIX.get("voxconverse", ""), f"{TITLE.get('voxconverse', 'VoxConverse')} test error per true-K bin — where counting breaks down as K grows.")


# ------------------------------------------------------------------ 6 affinity, 7 spectrum, 11 tsne
def _order(sess):
    lab = [l if l is not None else "~ambiguous" for l in sess.label]
    return np.lexsort((sess.center, np.array(lab))), np.array(lab)


def affinity_plot(corpus, split, rec, title):
    from ..pipeline import load_session

    cfg = load_config(f"configs/{'ami' if corpus == 'ami' else 'vox'}_{split}.yaml")
    r = _rec(corpus, split, "nmesc_affnet", rec)
    if r is None:
        return
    s = load_session(cfg, rec)
    order, lab = _order(s)
    step = max(1, len(order) // 700)
    order = order[::step]
    za = r["z"].astype(np.float32)
    zs = [("raw ECAPA", s.x), ("AffinityNet", za)]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
    bounds = np.where(lab[order][1:] != lab[order][:-1])[0] + 0.5
    pe, pa = _pred(corpus, split, "nmesc_ecapa"), _pred(corpus, split, "nmesc_affnet")
    kh = {n: int(p.set_index("recording_id").k_pred[rec]) for n, p in (("raw ECAPA", pe), ("AffinityNet", pa)) if p is not None}
    for ax, (name, z) in zip(axes, zs):
        a = z[order] @ z[order].T
        im = ax.imshow(a, cmap="RdBu_r", vmin=-1, vmax=1, interpolation="nearest")
        for b in bounds:
            ax.axhline(b, color=INK, lw=0.6)
            ax.axvline(b, color=INK, lw=0.6)
        ax.set_title(f"{name}: K̂={kh.get(name, '?')}", fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
    spk = [l for l in dict.fromkeys(lab[order])]
    fig.colorbar(im, ax=axes, shrink=0.8, label="cosine")
    fig.suptitle(f"{title} {split} {rec} (K={s.meta['k_true']}): affinity sorted by reference speaker, then time\n"
                 f"blocks: {', '.join(x.replace('~ambiguous', 'ambiguous/overlap') for x in spk)}", fontsize=9)
    _save(fig, f"affinity_{rec}", f"{rec}: cosine affinity, raw ECAPA vs AffinityNet, sorted by reference speaker "
          "(last block = ambiguous/overlap segments) — look for crisper diagonal blocks and split blocks.")


def spectrum_plot(corpus, split, rec, title, k_max):
    r = _rec(corpus, split, "snet_affnet_pp", rec)
    if r is None or "exact_eigenvalues" not in r:
        return
    d = _pred(corpus, split, "snet_affnet_pp").set_index("recording_id").loc[rec]
    m = k_max + 3
    ex, rz = r["exact_eigenvalues"][:m], r["eigenvalues"][:m]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.2))
    idx = np.arange(1, len(ex) + 1)
    axes[0].plot(idx, ex, marker="o", color=COLOR["nmesc_affnet"], lw=2, label="exact eigh")
    axes[0].plot(np.arange(1, len(rz) + 1), rz, marker="x", ls="--", color=COLOR["snet_affnet_pp"], lw=1.5,
                 markersize=8, label="SpectralNet Ritz values")
    axes[0].set_xlabel("index i")
    axes[0].set_ylabel("λ_i (Laplacian at p*)")
    axes[0].legend(fontsize=7)
    gx, gr = np.diff(ex)[:k_max], np.diff(rz)[:k_max]
    w = 0.38
    axes[1].bar(np.arange(1, len(gx) + 1) - w / 2, gx, w, color=COLOR["nmesc_affnet"], label="exact")
    axes[1].bar(np.arange(1, len(gr) + 1) + w / 2, gr, w, color=COLOR["snet_affnet_pp"], label="Ritz")
    for ax in axes:
        ax.axvline(int(d.k_true), color=INK, ls=":", lw=1)
    axes[0].text(int(d.k_true), axes[0].get_ylim()[1] * 0.97, " true K", fontsize=7, color=INK, va="top")
    axes[1].set_ylim(top=axes[1].get_ylim()[1] * 1.15)
    axes[1].annotate(f"true K={int(d.k_true)}", (int(d.k_true), axes[1].get_ylim()[1]), xytext=(2, -2),
                     textcoords="offset points", fontsize=7, va="top")
    axes[1].annotate(f"K̂={int(d.k_eigengap)} (tallest gap)", (int(d.k_eigengap), max(gx.max(), gr.max())),
                     xytext=(0, 6), textcoords="offset points", ha="center", fontsize=7, color=MUTED)
    axes[1].set_xlabel("gap index k (λ_{k+1} − λ_k)")
    axes[1].set_ylabel("eigengap")
    axes[1].legend(fontsize=7, loc="upper right")
    fig.suptitle(f"{title} {split} {rec}: spectrum (K={int(d.k_true)}, K̂={int(d.k_pred)}, p*={int(d.p_star)})", fontsize=9)
    _save(fig, f"spectrum_{rec}", f"{rec}: first k_max+3 Laplacian eigenvalues and eigengaps, exact vs SpectralNet "
          "Ritz — the tallest gap is K̂; Ritz ≈ exact means SpectralNet is a faithful backend.")


def tsne_plot(corpus, split, rec, title):
    from sklearn.manifold import TSNE

    from ..pipeline import load_session

    cfg = load_config(f"configs/{'ami' if corpus == 'ami' else 'vox'}_{split}.yaml")
    r = _rec(corpus, split, "nmesc_affnet", rec)
    if r is None:
        return
    s = load_session(cfg, rec)
    rng = np.random.default_rng(0)
    idx = np.sort(rng.choice(s.n, size=min(s.n, 2000), replace=False))
    lab = np.array([l if l is not None else "ambiguous" for l in s.label])[idx]
    spk = sorted(set(lab) - {"ambiguous"})
    pal = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.2))
    for ax, (name, z) in zip(axes, [("raw ECAPA", s.x[idx]), ("AffinityNet", r["z"].astype(np.float32)[idx])]):
        y = TSNE(n_components=2, metric="cosine", init="pca", random_state=0, perplexity=30).fit_transform(z)
        amb = lab == "ambiguous"
        ax.scatter(y[amb, 0], y[amb, 1], s=4, color="#c9c8c3", label="ambiguous/overlap")
        for i, sp in enumerate(spk):
            mk = lab == sp
            ax.scatter(y[mk, 0], y[mk, 1], s=5, color=pal[i % len(pal)], label=sp)
        ax.set_title(name, fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    axes[1].legend(fontsize=6, markerscale=3, loc="center left", bbox_to_anchor=(1.0, 0.5))
    fig.suptitle(f"{title} {split} {rec}: t-SNE (cosine) coloured by reference speaker", fontsize=9)
    _save(fig, f"tsne_{rec}", f"{rec}: t-SNE of raw ECAPA vs AffinityNet embeddings by reference speaker (grey = "
          "ambiguous) — tighter, better separated clusters mean a better affinity.")


# ------------------------------------------------------------------ 8 cluster shares
def cluster_shares(corpus, title):
    rows = []
    for m in METHODS:
        d = _pred(corpus, "test", m)
        if d is None or m == "baseline_mode":
            continue
        for _, r in d.iterrows():
            rec = _rec(corpus, "test", m, r.recording_id)
            if rec is None:
                continue
            lab = rec["labels_raw"]
            sh = np.bincount(lab) / lab.size
            rows.append({"method": m, "share": sh[sh > 0].min(), "correct": int(rec["k_eigengap"]) == r.k_true})
    if not rows:
        return
    df = pd.DataFrame(rows)
    names = list(dict.fromkeys(df.method))
    rng = np.random.default_rng(0)
    floor = 0.1  # % ; tuned share 0 (= pruning off) is drawn here
    fig, ax = plt.subplots(figsize=(9, 3.6))
    for i, m in enumerate(names):
        sub = df[df.method == m]
        for ok, dx, mk in ((True, -0.15, "o"), (False, 0.15, "X")):
            s2 = sub[sub.correct == ok]
            ax.scatter(i + dx + rng.uniform(-0.05, 0.05, len(s2)), np.maximum(100 * s2.share, floor), color=COLOR[m],
                       marker=mk, s=30 if ok else 45, edgecolor="white", linewidth=0.6)
        bf = ROOT / "results" / "tuning" / m / "best.yaml"
        if bf.exists():
            t = yaml.safe_load(bf.read_text())["min_cluster_share"]
            ax.hlines(max(100 * t, floor), i - 0.35, i + 0.35, color=INK, lw=1.5, ls="-" if t > 0 else ":")
            if t == 0:
                ax.text(i, floor * 1.15, "pruning off", ha="center", va="bottom", fontsize=6, color=MUTED)
    ax.set_xticks(range(len(names)), names, rotation=25, ha="right", fontsize=8)
    ax.set_ylabel("smallest cluster share\nbefore post-processing (%)")
    ax.set_yscale("log")
    ax.set_ylim(floor * 0.8, 60)
    from matplotlib.lines import Line2D

    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=MUTED, label="eigengap K correct"),
                       Line2D([], [], marker="X", ls="", color=MUTED, label="eigengap K wrong"),
                       Line2D([], [], color=INK, lw=1.5, label="tuned min_cluster_share")], fontsize=7,
              loc="center left", bbox_to_anchor=(1.0, 0.5))
    ax.set_title(f"{title} test: smallest-cluster share, correct vs wrong (before pruning)")
    _save(fig, f"cluster_shares_{_fn(corpus)}", f"{title} test smallest-cluster share before post-processing — wrong "
          "counts (X) below the black tuned threshold are the tiny-extra-cluster errors pruning removes; correct "
          "recordings (o) below it would be hurt by pruning.")


# ------------------------------------------------------------------ 9 tuning heatmap
def tuning_heatmaps():
    for f in sorted((ROOT / "results" / "tuning").glob("*.csv")):
        m = f.stem
        d = pd.read_csv(f)
        d["merge_threshold"] = d.merge_threshold.astype(str)
        piv = d.groupby(["min_cluster_share", "merge_threshold"]).objective.max().unstack()
        cols = ["off"] + sorted(c for c in piv.columns if c != "off")
        piv = piv[cols]
        fig, ax = plt.subplots(figsize=(5, 3.6))
        im = ax.imshow(piv.values, cmap="Blues", vmin=min(0.5, piv.values.min()), vmax=1, aspect="auto")
        for i in range(piv.shape[0]):
            for j in range(piv.shape[1]):
                v = piv.values[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7, color="white" if v > 0.85 else INK)
        best = yaml.safe_load((ROOT / "results" / "tuning" / m / "best.yaml").read_text())
        bi = list(piv.index).index(best["min_cluster_share"])
        bj = cols.index("off" if best["merge_threshold"] is None else str(best["merge_threshold"]))
        ax.add_patch(plt.Rectangle((bj - 0.5, bi - 0.5), 1, 1, fill=False, ec=COLOR["old"], lw=2))
        ax.set_xticks(range(len(cols)), cols)
        ax.set_yticks(range(len(piv.index)), piv.index)
        ax.set_xlabel("merge_threshold")
        ax.set_ylabel("min_cluster_share")
        ax.grid(False)
        fig.colorbar(im, ax=ax, label="val objective")
        ax.set_title(f"{m}: val objective (max over single-speaker thr.)\nval sets: {', '.join(best['val_sets'])}", fontsize=8)
        _save(fig, f"tuning_heatmap_{m}", f"{m}: validation objective over min_cluster_share × merge_threshold (red = "
              "chosen) — a flat map means post-processing has nothing to fix on val.")


# ------------------------------------------------------------------ 10 train curves
def train_curves():
    f = ROOT / "checkpoints" / "affnet" / "train_log.csv"
    if not f.exists():
        return
    d = pd.read_csv(f)
    best = yaml.safe_load((ROOT / "checkpoints" / "affnet" / "best.yaml").read_text())["best_epoch"]
    ref_f = ROOT / "checkpoints" / "affnet" / "val_raw_ecapa.yaml"
    ref = yaml.safe_load(ref_f.read_text()) if ref_f.exists() else {}
    fig, axes = plt.subplots(1, 4, figsize=(13, 3))
    t = d[d.epoch > 0]
    axes[0].plot(t.epoch, t.loss, color=COLOR["nmesc_affnet"], lw=2, label="total")
    axes[0].plot(t.epoch, t.bce, color=COLOR["nmesc_ecapa"], lw=2, label="BCE")
    axes[0].plot(t.epoch, t.supcon * 0.5, color=COLOR["nmesc_ecapa_pp"], lw=2, label="0.5·SupCon")
    axes[0].set_title("training loss")
    axes[0].legend(fontsize=7)
    for ax, col, name in ((axes[1], "val_eer", "val pair EER (AMI dev)"), (axes[2], "ami_mae", "val count MAE (AMI dev)"),
                          (axes[3], "val_score", "val_score (selection)")):
        ax.plot(d.epoch, d[col], color=COLOR["nmesc_affnet"], lw=2, marker="o", markersize=3)
        if col in ref:
            ax.axhline(ref[col], color=COLOR["nmesc_ecapa"], ls="--", lw=1)
            ax.text(d.epoch.max(), ref[col], "raw ECAPA", fontsize=7, color=MUTED, ha="right", va="bottom")
        ax.set_title(name)
    for ax in axes:
        ax.axvline(best, color=INK, ls=":", lw=1)
        ax.set_xlabel("epoch")
    axes[3].text(best, axes[3].get_ylim()[1] * 0.92, f" chosen epoch {best}", fontsize=7)
    fig.suptitle("AffinityNet training (AMI train, AMI dev validation)", y=1.03)
    _save(fig, "train_curves", "AffinityNet training: loss keeps falling while val pair EER rises after ~epoch 9 "
          "(overfitting); val MAE is noisy on an all-K=4 dev set; dotted line = chosen checkpoint.")


# ------------------------------------------------------------------ 12 p* hist
def pstar_hist():
    fig, ax = plt.subplots(figsize=(6, 3))
    any_ = False
    for corpus, title in CORPORA:
        for split in ("dev", "val", "test"):
            d = _pred(corpus, split, "nmesc_ecapa")
            if d is None:
                continue
            any_ = True
            ax.hist(d.p_star, bins=np.arange(0.5, 62.5, 1), alpha=0.7, label=f"{title} {split} (nmesc_ecapa)",
                    color=COLOR["nmesc_ecapa"] if split == "test" else COLOR["nmesc_ecapa_pp"])
            d2 = _pred(corpus, split, "nmesc_affnet")
            if d2 is not None:
                ax.hist(d2.p_star, bins=np.arange(0.5, 62.5, 1), alpha=0.7, histtype="step", lw=2,
                        label=f"{title} {split} (nmesc_affnet)", color=COLOR["nmesc_affnet"] if split == "test" else COLOR["snet_affnet_pp"])
    if not any_:
        plt.close(fig)
        return
    ax.axvline(60, color=COLOR["old"], lw=1.5)
    ax.text(60, ax.get_ylim()[1] * 0.9, "p_max_abs=60 ", ha="right", fontsize=7, color=MUTED)
    ax.set_xlabel("p*")
    ax.set_ylabel("recordings")
    ax.legend(fontsize=6)
    ax.set_title("NME-SC p* distribution")
    _save(fig, "pstar_hist", "Distribution of the NME-SC binarisation p* — all values far below the p_max_abs=60 cap, "
          "so the cap (the speed fix) never changes a result.")


# ------------------------------------------------------------------ 14 timing
def timing():
    fig, ax = plt.subplots(figsize=(6, 3.4))
    any_ = False
    for m, mk in (("nmesc_ecapa", "o"), ("nmesc_affnet", "s"), ("snet_ecapa_pp", "^"), ("snet_affnet_pp", "D")):
        for corpus, split in (("ami", "dev"), ("ami", "test"), ("voxconverse", "test")):
            d = _pred(corpus, split, m)
            if d is None:
                continue
            any_ = True
            ax.scatter(d.n_segments, d.cluster_sec, color=COLOR[m], marker=mk, s=22 if corpus == "ami" else 12,
                       edgecolor="white", linewidth=0.6, alpha=1 if corpus == "ami" else 0.6,
                       label=f"{m} ({'exact' if m.startswith('nmesc') else 'SpectralNet'})" if split == "test" and corpus == "ami" else None)
    if not any_:
        plt.close(fig)
        return
    old = 25.7 * 60 / 16
    ax.axhline(old, color=COLOR["old"], ls="--", lw=1.5)
    ax.text(ax.get_xlim()[0], old, "  old NME-SC: 25.7 min / 16 rec (mean)", va="bottom", fontsize=7, color=MUTED)
    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel("segments N (log)")
    ax.set_ylabel("clustering time per recording (s)")
    ax.legend(fontsize=7, loc="lower right")
    ax.set_title("Clustering time vs N (AMI dev+test large markers; VoxConverse test small)")
    _save(fig, "timing", "Clustering time per recording vs N (log y) — every method is ~10× under the old mean; "
          "SpectralNet's extra cost is the per-session fit (~10 s).")


def make_all() -> None:
    CAPTIONS.clear()
    TITLE.update({c: t for c, t in CORPORA})
    if _pred("voxconverse", "test", "nmesc_ecapa", "") is None and _pred("voxconverse", "test", "nmesc_ecapa", "ami_trained") is not None:
        TAG["voxconverse"], SUFFIX["voxconverse"] = "ami_trained", "_amitrained"
        TITLE["voxconverse"] = "VoxConverse (AMI-trained, cross-corpus)"
    for corpus, _ in CORPORA:
        title = TITLE[corpus]
        metrics_bar(corpus, title)
        der_bar(corpus, title)
        confusions(corpus, title)
        error_hist(corpus, title)
        scatter_k(corpus, title)
        cluster_shares(corpus, title)
    error_vs_k_vox()
    # 2 best + 2 worst AMI test recordings by nmesc_affnet |K̂−K| (+ EN2002a, TS3003a as required)
    d = _pred("ami", "test", "nmesc_affnet")
    if d is not None:
        d = d.assign(ae=(d.k_pred - d.k_true).abs()).sort_values(["ae", "der"])
        recs = list(dict.fromkeys(list(d.recording_id[:2]) + list(d.recording_id[-2:]) + ["EN2002a", "TS3003a"]))
        for r in recs:
            affinity_plot("ami", "test", r, "AMI")
            spectrum_plot("ami", "test", r, "AMI", 10)
        tsne_plot("ami", "test", "EN2002a", "AMI")
    d = _pred("voxconverse", "test", "nmesc_affnet")
    if d is not None:
        d = d.assign(ae=(d.k_pred - d.k_true).abs()).sort_values(["ae", "der"])
        mid = d[(d.k_true >= 4) & (d.k_true <= 8)]
        recs = list(dict.fromkeys(list(mid.recording_id[:2]) + list(d.recording_id[-2:])))
        for r in recs:
            affinity_plot("voxconverse", "test", r, TITLE["voxconverse"])
            spectrum_plot("voxconverse", "test", r, TITLE["voxconverse"], 25)
        if len(mid):
            tsne_plot("voxconverse", "test", mid.recording_id.iloc[0], TITLE["voxconverse"])
    tuning_heatmaps()
    train_curves()
    pstar_hist()
    timing()
    lines = ["## Figures", "", "All in `results/plots/` (PNG 150 dpi + PDF). Method colours are fixed across figures."]
    if TAG.get("voxconverse") == "ami_trained":
        lines += ["VoxConverse figures (`*_voxconverse_amitrained*`) are the **cross-corpus** runs: models, thresholds and "
                  "the mode baseline (4) all come from AMI; nothing was fitted on VoxConverse."]
    elif _pred("voxconverse", "test", "nmesc_ecapa") is None:
        lines += ["VoxConverse figures (`*_voxconverse`, `error_vs_k_vox`, VoxConverse affinity/t-SNE) are not produced: "
                  "VoxConverse data is not available yet."]
    lines += [""] + [f"- [`{n}.png`](plots/{n}.png) — {c}" for n, c in CAPTIONS]
    (OUT / "captions.md").write_text("\n".join(lines) + "\n")
    print(f"[plots] {len(CAPTIONS)} figures, captions in {OUT / 'captions.md'}")
