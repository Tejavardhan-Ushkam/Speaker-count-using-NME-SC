"""SpectralNet v2 out-of-sample test (prompt §4.5): on 3 val recordings, fit on 90 % of the
segments, embed the held-out 10 % with the frozen parametric map, and compare their labels
with the full-session run (labels matched by Hungarian assignment on the shared segments).
Target: agreement >= 95 %.

    python scripts/spectralnet_oos.py --config configs/ami_dev.yaml --method snet_affnet_pp
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from scipy.optimize import linear_sum_assignment  # noqa: E402
from sklearn.cluster import KMeans  # noqa: E402

from speakercount.cluster.nmesc import binarize, eigengap_stats, search_p  # noqa: E402
from speakercount.cluster.run import Embedder  # noqa: E402
from speakercount.cluster.spectralnet import fit_spectralnet, transform  # noqa: E402
from speakercount.config import ROOT, load_config  # noqa: E402
from speakercount.pipeline import load_split  # noqa: E402


def _rownorm(a):
    return a / np.maximum(np.linalg.norm(a, axis=1, keepdims=True), 1e-12)


def run(z, cfg):
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    zt = torch.as_tensor(z, dtype=torch.float32, device=dev)
    a = zt @ zt.T
    a.fill_diagonal_(0.0)
    sr = search_p(a, cfg.clustering)
    w = binarize(sr.order, sr.p_star, len(z), torch.float32, dev)
    fit = fit_spectralnet(z, w, cfg, seed=cfg.seed)
    k, *_ = eigengap_stats(fit["ritz"], min(cfg.clustering.k_max, len(z) - 1))
    km = KMeans(n_clusters=max(k, 1), n_init=cfg.clustering.kmeans_n_init, random_state=cfg.seed)
    labels = km.fit_predict(_rownorm(fit["Y"][:, :k])) if k > 1 else np.zeros(len(z), int)
    return fit, k, km, labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/ami_dev.yaml")
    ap.add_argument("--method", default="snet_affnet_pp")
    ap.add_argument("--recordings", nargs="*", default=None)
    args = ap.parse_args()
    cfg = load_config(args.config, method=args.method)
    sessions = load_split(cfg, args.recordings)
    if not args.recordings:
        sessions = sessions[:3]
    emb = Embedder(cfg)
    lines = [f"# SpectralNet v2 out-of-sample test — {args.method}, {cfg.dataset.corpus}/{cfg.dataset.split}", "",
             "| rec | N | K (full) | K (90 %) | held-out | agreement |", "|---|---|---|---|---|---|"]
    agree_all = []
    for s in sessions:
        z = emb(s)
        _, k_full, _, lab_full = run(z, cfg)
        rng = np.random.default_rng(0)
        hold = np.zeros(len(z), bool)
        hold[rng.choice(len(z), size=max(1, len(z) // 10), replace=False)] = True
        fit, k90, km, lab90 = run(z[~hold], cfg)
        y_hold = transform(fit, z[hold])[:, :k90]
        lab_hold = km.predict(_rownorm(y_hold)) if k90 > 1 else np.zeros(hold.sum(), int)
        # match 90 %-run labels to full-run labels on the shared (in-sample) segments
        kk = max(lab_full.max(), lab90.max()) + 1
        conf = np.zeros((kk, kk))
        np.add.at(conf, (lab90, lab_full[~hold]), 1)
        r, c = linear_sum_assignment(-conf)
        mapping = dict(zip(r, c))
        mapped = np.array([mapping.get(v, -1) for v in lab_hold])
        agree = float(np.mean(mapped == lab_full[hold]))
        agree_all.append(agree)
        lines.append(f"| {s.rec} | {len(z)} | {k_full} | {k90} | {int(hold.sum())} | {agree:.3f} |")
        print(lines[-1], flush=True)
    lines += ["", f"Mean held-out label agreement: **{np.mean(agree_all):.3f}** (target >= 0.95).", ""]
    out = ROOT / "results" / "spectralnet_oos" / f"{args.method}_{cfg.dataset.corpus}_{cfg.dataset.split}.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
