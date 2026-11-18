"""Ablation: the old Siamese network re-implemented with ONLY flaws 1-2 fixed (prompt §7).

Kept from the old project: MLP 192->128->128->64, 2 positive + 2 random negative pairs per
anchor within each recording, most-overlap labels, contrastive loss with margin 1, 30 epochs,
Adam lr 1e-3, batch 128, no validation.
Fixed: (1) no ReLU on the output layer; (2) the contrastive loss uses the cosine distance
1 - cos(z_i, z_j) of L2-normalised outputs, i.e. the same metric as inference.
"""

from __future__ import annotations

import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..config import Cfg, dump_yaml, git_commit, load_config, resolve_path
from ..embedding import resolve_device


class Siamese(nn.Module):
    def __init__(self, in_dim=192, hiddens=(128, 128, 64)):
        super().__init__()
        layers, d = [], in_dim
        for i, h in enumerate(hiddens):
            layers.append(nn.Linear(d, h))
            if i < len(hiddens) - 1:  # flaw 1 fixed: no ReLU after the last layer
                layers.append(nn.ReLU())
            d = h
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return F.normalize(self.net(x), dim=-1)


def _pairs(sessions, rng, n_pos=2, n_neg=2):
    a, b, y = [], [], []
    offset = 0
    for s in sessions:
        lab = np.array([l if l is not None else "" for l in s.label_most])
        valid = np.where(lab != "")[0]
        by = {}
        for i in valid:
            by.setdefault(lab[i], []).append(i)
        by = {k: np.array(v) for k, v in by.items()}
        for i in valid:
            same = by[lab[i]]
            if len(same) > 1:
                for j in rng.choice(same, n_pos):
                    a.append(offset + i); b.append(offset + j); y.append(1)
            others = valid[lab[valid] != lab[i]]
            if len(others):
                for j in rng.choice(others, n_neg):
                    a.append(offset + i); b.append(offset + j); y.append(0)
        offset += s.n
    return np.array(a), np.array(b), np.array(y, np.float32)


def train_siamese(cfg: Cfg) -> None:
    from ..pipeline import load_split
    from ..rttm import available_configs

    a = cfg.affnet
    torch.manual_seed(cfg.seed)
    rng = np.random.default_rng(cfg.seed)
    dev = resolve_device(a.device)
    out_dir = resolve_path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dump_yaml(cfg, out_dir / "config_resolved.yaml")
    sessions = []
    for tp in available_configs(list(a.train_configs), "train-siamese"):
        sessions += load_split(load_config(tp))
    try:
        x = torch.as_tensor(np.concatenate([s.x for s in sessions]), device=dev)
        torch.empty(256 * 2**20, dtype=torch.uint8, device=dev)  # headroom probe (shared GPU)
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        dev = "cpu"
        print("[train-siamese] GPU nearly full: training on CPU")
        x = torch.as_tensor(np.concatenate([s.x for s in sessions]), device=dev)
    model = Siamese(x.shape[1]).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    t0 = time.time()
    for epoch in range(30):
        ia, ib, y = _pairs(sessions, rng)
        perm = rng.permutation(len(y))
        ia, ib, y = (torch.as_tensor(v[perm], device=dev) for v in (ia, ib, y))
        tot = 0.0
        for lo in range(0, len(y), 128):
            za, zb = model(x[ia[lo:lo + 128]]), model(x[ib[lo:lo + 128]])
            d = 1.0 - (za * zb).sum(-1)  # flaw 2 fixed: cosine distance, as at inference
            yy = y[lo:lo + 128]
            loss = (yy * d.pow(2) + (1 - yy) * torch.clamp(1.0 - d, min=0).pow(2)).mean()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            tot += float(loss) * len(yy)
        print(f"[train-siamese] epoch {epoch + 1}/30 loss {tot / len(y):.4f} ({time.time() - t0:.0f} s)", flush=True)
    torch.save({"model": model.state_dict(), "in_dim": x.shape[1], "git_commit": git_commit()}, out_dir / "best.pt")


class SiameseInference:
    def __init__(self, cfg: Cfg):
        ck = torch.load(resolve_path(cfg.affinity.checkpoint), map_location="cpu", weights_only=False)
        self.model = Siamese(ck["in_dim"])
        self.model.load_state_dict(ck["model"])
        self.dev = resolve_device(cfg.affnet.device)
        self.model.to(self.dev).eval()

    @torch.no_grad()
    def __call__(self, x: np.ndarray) -> np.ndarray:
        return self.model(torch.as_tensor(x, dtype=torch.float32, device=self.dev)).cpu().numpy()
