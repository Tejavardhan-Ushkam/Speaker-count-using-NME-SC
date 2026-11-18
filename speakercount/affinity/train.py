"""AffinityNet training with per-epoch validation and early stopping (prompt §4.3).

val_score = 0.5 * MAE(AMI dev) + 0.5 * mean relative error(Vox val); a val set that is not
available is dropped and the other gets weight 1 (AMI-only mode). Lower is better; ties are
broken by the mean pairwise EER (lower), which is logged with every epoch.
"""

from __future__ import annotations

import csv
import math
import random
import time

import numpy as np
import torch
from sklearn.metrics import roc_curve

from ..cluster.run import cluster_session
from ..config import Cfg, dump_yaml, git_commit, load_config, resolve_path
from ..embedding import resolve_device
from ..eval.metrics import count_metrics
from ..pipeline import load_split
from ..rttm import available_configs
from .data import ChunkSampler
from .infer import embed
from .loss import AffinityLoss
from .model import AffinityNet

IDENTITY_PP = {"min_cluster_share": 0.0, "merge_threshold": None, "single_speaker_threshold": None}


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def pair_eer(z: np.ndarray, labels: list, max_pairs: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Cosine scores and same-speaker targets of (sub-sampled) clean pairs of one recording."""
    idx = np.array([i for i, l in enumerate(labels) if l is not None])
    if idx.size < 2:
        return np.zeros(0), np.zeros(0)
    lab = np.array([labels[i] for i in idx])
    n = idx.size
    if n * (n - 1) // 2 <= max_pairs:
        i, j = np.triu_indices(n, 1)
    else:
        i = rng.integers(0, n, max_pairs)
        j = rng.integers(0, n, max_pairs)
        ok = i != j
        i, j = i[ok], j[ok]
    zi = z[idx]
    return np.einsum("ij,ij->i", zi[i], zi[j]), (lab[i] == lab[j]).astype(np.int8)


def eer(scores: np.ndarray, y: np.ndarray) -> float:
    if scores.size == 0 or y.min() == y.max():
        return float("nan")
    fpr, tpr, _ = roc_curve(y, scores)
    fnr = 1 - tpr
    k = int(np.nanargmin(np.abs(fnr - fpr)))
    return float((fpr[k] + fnr[k]) / 2)


class Validator:
    def __init__(self, val_paths: list[str], cfg: Cfg):
        self.sets = []
        for vp in val_paths:
            vcfg = load_config(vp, method="nmesc_affnet",
                               overrides={"clustering": {"eig_solver": cfg.affnet.val_eig_solver}})
            self.sets.append((vcfg, load_split(vcfg)))
        self.max_pairs = cfg.affnet.eer_max_pairs

    def __call__(self, embed_fn) -> dict:
        out, score_terms, eers = {}, [], []
        for vcfg, sessions in self.sets:
            tag = "ami" if vcfg.dataset.corpus == "ami" else "vox"
            rng = np.random.default_rng(0)
            sc, ys, kt, kp = [], [], [], []
            for s in sessions:
                z = embed_fn(s)
                a, b = pair_eer(z, s.label, self.max_pairs, rng)
                sc.append(a)
                ys.append(b)
                res = cluster_session(s, z, vcfg, IDENTITY_PP)
                kt.append(s.meta["k_true"])
                kp.append(res["k_pred"])
            e = eer(np.concatenate(sc), np.concatenate(ys))
            m = count_metrics(kt, kp, vcfg.evaluation.rel_error_tol)
            out.update({f"{tag}_eer": e, f"{tag}_exact": m["exact"], f"{tag}_mae": m["mae"],
                        f"{tag}_signed": m["signed"], f"{tag}_rel_err": m["rel_err_mean"]})
            score_terms.append(m["mae"] if tag == "ami" else m["rel_err_mean"])
            eers.append(e)
        out["val_score"] = float(np.mean(score_terms))
        out["val_eer"] = float(np.nanmean(eers))
        return out


def _step(model, crit, opt, params, batch, dev, bf16, grad_clip):
    x, t, mask, labels = (v.to(dev) for v in batch)
    with torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=bf16):
        z = model(x, t, mask)
    out = crit(z.float(), labels)
    opt.zero_grad(set_to_none=True)
    out["loss"].backward()
    torch.nn.utils.clip_grad_norm_(params, grad_clip)
    opt.step()
    return out


def train(cfg: Cfg) -> None:
    a = cfg.affnet
    seed_all(cfg.seed)
    dev = torch.device(resolve_device(a.device))
    out_dir = resolve_path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dump_yaml(cfg, out_dir / "config_resolved.yaml")
    (out_dir / "git_commit.txt").write_text(git_commit() + "\n")

    train_paths = available_configs(list(a.train_configs), "train-affnet")
    val_paths = available_configs(list(a.val_configs), "train-affnet val")
    corpora: dict = {}
    for tp in train_paths:
        tcfg = load_config(tp)
        corpora.setdefault(tcfg.dataset.corpus, []).extend(load_split(tcfg))
    sampler = ChunkSampler(corpora, a, seed=cfg.seed)
    validator = Validator(val_paths, cfg)
    print(f"[train-affnet] train {train_paths} ({sampler.n_sessions()} sessions), val {val_paths}")

    model = AffinityNet(**{k: a[k] for k in ("in_dim", "d_model", "n_layers", "n_heads", "ffn", "dropout",
                                               "time_encoding", "time_min_period", "time_max_period", "alpha_init")}).to(dev)
    crit = AffinityLoss(a.logit_w_init, a.logit_b_init, a.loss_bce_weight, a.loss_supcon_weight,
                        a.supcon_temperature).to(dev)
    params = list(model.parameters()) + list(crit.parameters())
    opt = torch.optim.AdamW(params, lr=a.lr, weight_decay=a.weight_decay)
    steps_per_epoch = math.ceil(sampler.n_sessions() * a.chunks_per_session / a.batch_chunks)
    total = steps_per_epoch * a.max_epochs

    def lr_at(step: int) -> float:
        if step < a.warmup_steps:
            return a.lr * (step + 1) / a.warmup_steps
        prog = (step - a.warmup_steps) / max(1, total - a.warmup_steps)
        return a.lr * 0.5 * (1 + math.cos(math.pi * min(1.0, prog)))

    bf16 = dev.type == "cuda" and torch.cuda.is_bf16_supported()

    def embed_fn(s):
        model.eval()
        args = (s.x, s.center, cfg.affinity.infer_max_full, cfg.affinity.infer_chunk, cfg.affinity.infer_stride)
        try:
            return embed(model, *args)
        except torch.cuda.OutOfMemoryError:  # validate this session with a CPU copy
            import copy

            torch.cuda.empty_cache()
            return embed(copy.deepcopy(model).cpu(), *args)

    log_f = out_dir / "train_log.csv"
    fields = None
    best, best_key, bad = None, (float("inf"), float("inf")), 0
    # epoch 0 = untrained model (alpha 0.1 residual, ~ raw ECAPA); plus raw ECAPA reference
    ref = validator(lambda s: s.x)
    print(f"[train-affnet] raw ECAPA reference on val: {ref}")
    dump_yaml(ref, out_dir / "val_raw_ecapa.yaml")
    step = 0
    for epoch in range(0, a.max_epochs + 1):
        t0 = time.time()
        losses = {"loss": [], "bce": [], "supcon": []}
        if epoch > 0:
            model.train()
            for _ in range(steps_per_epoch):
                batch = sampler.batch(a.batch_chunks)
                for g in opt.param_groups:
                    g["lr"] = lr_at(step)
                try:
                    out = _step(model, crit, opt, params, batch, dev, bf16, a.grad_clip)
                except torch.cuda.OutOfMemoryError:  # shared GPU full: continue training on CPU
                    torch.cuda.empty_cache()
                    print("[train-affnet] GPU out of memory: moving training to CPU", flush=True)
                    dev, bf16 = torch.device("cpu"), False
                    model.to(dev)
                    crit.to(dev)
                    for st in opt.state.values():
                        for k, v in st.items():
                            if torch.is_tensor(v):
                                st[k] = v.to(dev)
                    out = _step(model, crit, opt, params, batch, dev, bf16, a.grad_clip)
                step += 1
                for k in losses:
                    losses[k].append(float(out[k]))
        t_train = time.time() - t0
        val = validator(embed_fn)
        row = {"epoch": epoch, "step": step, "lr": lr_at(max(0, step - 1)) if epoch else 0.0,
               "loss": np.mean(losses["loss"]) if losses["loss"] else float("nan"),
               "bce": np.mean(losses["bce"]) if losses["bce"] else float("nan"),
               "supcon": np.mean(losses["supcon"]) if losses["supcon"] else float("nan"),
               "alpha": float(model.alpha), "w": float(torch.nn.functional.softplus(crit.w_raw)),
               "b": float(crit.b), **val, "time_train_sec": t_train, "time_val_sec": time.time() - t0 - t_train}
        with open(log_f, "w" if fields is None else "a", newline="") as f:
            if fields is None:
                fields = list(row)
                csv.DictWriter(f, fieldnames=fields).writeheader()
            csv.DictWriter(f, fieldnames=fields).writerow(row)
        key = (val["val_score"], val["val_eer"])
        state = {"model": model.state_dict(), "hparams": model.hparams, "loss": crit.state_dict(),
                 "epoch": epoch, "step": step, "val": val, "git_commit": git_commit()}
        torch.save(state, out_dir / "last.pt")
        improved = key < best_key
        if improved:
            best_key, best, bad = key, epoch, 0
            torch.save(state, out_dir / "best.pt")
        elif epoch > 0:
            bad += 1
        print(f"[train-affnet] epoch {epoch:2d} loss {row['loss']:.4f} (bce {row['bce']:.4f} supcon {row['supcon']:.4f}) "
              f"alpha {row['alpha']:.3f} | " + " ".join(f"{k} {v:.4f}" for k, v in val.items())
              + f" | {'*best*' if improved else f'no improvement {bad}/{a.patience}'} "
              f"({t_train:.0f}+{row['time_val_sec']:.0f} s)", flush=True)
        if bad >= a.patience:
            print(f"[train-affnet] early stop at epoch {epoch}; best epoch {best}")
            break
    dump_yaml({"best_epoch": best, "val_score": best_key[0], "val_eer": best_key[1]}, out_dir / "best.yaml")
