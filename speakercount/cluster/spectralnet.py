"""SpectralNet v2 (Shaham et al. 2018, fixed per prompt §4.5).

f: z -> Y~ (MLP 192-256-256-m, ReLU hidden, linear output), m = k_max + 1
orthonormalisation: Y = Y~ (Lchol^-1)^T sqrt(N), Lchol = chol(Y~^T Y~ + jitter I) -> Y^T Y = N I
loss: trace(Y^T L Y) / N on the NME-SC sparse affinity W at p* (full batch, one session)
Rayleigh-Ritz: M = Y^T L Y / N, eigh(M) -> Ritz values (K from their eigengap) and rotation.
After fitting, the Cholesky factor and rotation are frozen: the map applies to new segments.
"""

from __future__ import annotations

import time

import numpy as np
import torch
import torch.nn as nn

from ..config import Cfg, resolve_path
from ..embedding import resolve_device


class SpecNet(nn.Module):
    def __init__(self, in_dim: int, hidden: list[int], m: int):
        super().__init__()
        layers, d = [], in_dim
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU()]
            d = h
        layers.append(nn.Linear(d, m))  # linear output
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


def orthonorm_factor(yt: torch.Tensor, jitter: float) -> torch.Tensor:
    """Returns R = (Lchol^-1)^T * sqrt(N) so that Y = Y~ R has Y^T Y = N I."""
    n, m = yt.shape
    g = yt.T @ yt + jitter * torch.eye(m, dtype=yt.dtype, device=yt.device)
    lc = torch.linalg.cholesky(g)
    inv = torch.linalg.solve_triangular(lc, torch.eye(m, dtype=yt.dtype, device=yt.device), upper=False)
    return inv.T * (n ** 0.5)


class LapOp:
    """Sparse Laplacian-vector products for W (dense or sparse torch input)."""

    def __init__(self, w: torch.Tensor, kind: str):
        w = w.double()
        self.kind = kind
        self.deg = w.sum(1) if not w.is_sparse else torch.sparse.sum(w, 1).to_dense()
        import warnings

        with warnings.catch_warnings():  # "sparse CSR support is in beta" (harmless)
            warnings.simplefilter("ignore")
            self.w = w.to_sparse_csr()
        self.inv_sqrt = self.deg.clamp_min(1e-12).rsqrt()

    def __matmul__(self, y: torch.Tensor) -> torch.Tensor:
        y = y.double()
        if self.kind == "unnormalized":
            return self.deg[:, None] * y - self.w @ y
        s = self.inv_sqrt[:, None]
        return y - s * (self.w @ (s * y))


def _loss(net, x, lap, jitter):
    yt = net(x).double()
    r = orthonorm_factor(yt, jitter)
    y = yt @ r
    return torch.trace(y.T @ (lap @ y)) / y.shape[0], y, r


def train_on(net, opt, x, lap, cfg_s, max_steps, tol, patience):
    prev, calm, steps = None, 0, 0
    for steps in range(1, max_steps + 1):
        loss, _, _ = _loss(net, x, lap, cfg_s.jitter)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        v = float(loss)
        if prev is not None and abs(prev - v) / max(abs(prev), 1e-12) < tol:
            calm += 1
            if calm >= patience:
                break
        else:
            calm = 0
        prev = v
    return steps


def pretrained_path(cfg: Cfg) -> str:
    p = resolve_path(cfg.spectralnet.pretrained)
    m = cfg.clustering.k_max + 1
    return str(p.with_name(f"{p.stem}_{cfg.affinity.source}_{cfg.clustering.laplacian}_m{m}{p.suffix}"))


_PRETRAINED_CACHE: dict = {}


def get_pretrained(cfg: Cfg, in_dim: int):
    """Network pre-trained on the corpus' training sessions (50 steps per session, random order)."""
    path = pretrained_path(cfg)
    if path in _PRETRAINED_CACHE:
        return _PRETRAINED_CACHE[path]
    from pathlib import Path

    s = cfg.spectralnet
    m = cfg.clustering.k_max + 1
    dev = "cpu"  # one-off pre-training runs on CPU: robust on a shared, nearly full GPU
    if not Path(path).exists():
        from ..config import load_config
        from ..pipeline import load_split
        from .nmesc import binarize, search_p
        from .run import Embedder

        t0 = time.time()
        tcfg = load_config(cfg.dataset.train_config, overrides={"affinity": dict(cfg.affinity),
                                                                "clustering": dict(cfg.clustering)})
        sessions = load_split(tcfg)
        emb = Embedder(cfg)
        torch.manual_seed(cfg.seed)
        net = SpecNet(in_dim, list(s.hidden), m).to(dev).double()
        opt = torch.optim.Adam(net.parameters(), lr=s.lr)
        rng = np.random.default_rng(cfg.seed)
        c = tcfg.clustering
        for i in rng.permutation(len(sessions)):
            sess = sessions[i]
            z = emb(sess)
            zt = torch.as_tensor(z, dtype=torch.float32, device=dev)
            aff = zt @ zt.T
            aff.fill_diagonal_(0.0)
            sr = search_p(aff, c)
            w = binarize(sr.order, sr.p_star, len(z), torch.float32, dev)
            train_on(net, opt, zt.double(), LapOp(w, c.laplacian), s, s.pretrain_steps_per_session, 0.0, 10**9)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save({"model": net.state_dict(), "in_dim": in_dim, "m": m, "hidden": list(s.hidden),
                    "time_sec": time.time() - t0, "n_sessions": len(sessions)}, path)
        print(f"[spectralnet] pre-trained on {len(sessions)} sessions in {time.time() - t0:.0f} s -> {path}")
    ck = torch.load(path, map_location="cpu", weights_only=False)
    _PRETRAINED_CACHE[path] = ck
    return ck


def fit_spectralnet(z: np.ndarray, w: torch.Tensor, cfg: Cfg, seed: int = 0, warm_start: bool | None = None,
                    device: str | None = None) -> dict:
    try:
        return _fit(z, w, cfg, seed, warm_start, device or resolve_device(cfg.spectralnet.device))
    except torch.cuda.OutOfMemoryError:  # shared GPU full: same fit on CPU (same seed)
        torch.cuda.empty_cache()
        print("[spectralnet] GPU out of memory: fit moved to CPU")
        return _fit(z, w.cpu(), cfg, seed, warm_start, "cpu")


def _fit(z, w, cfg, seed, warm_start, dev) -> dict:
    s = cfg.spectralnet
    m = min(cfg.clustering.k_max + 1, z.shape[0] - 1)
    warm = s.warm_start if warm_start is None else warm_start
    torch.manual_seed(seed)
    net = SpecNet(z.shape[1], list(s.hidden), cfg.clustering.k_max + 1).to(dev).double()
    if warm:
        ck = get_pretrained(cfg, z.shape[1])
        net.load_state_dict(ck["model"])
    if m < cfg.clustering.k_max + 1:  # tiny session: truncate the output layer
        last = net.net[-1]
        new = nn.Linear(last.in_features, m).to(dev).double()
        with torch.no_grad():
            new.weight.copy_(last.weight[:m])
            new.bias.copy_(last.bias[:m])
        net.net[-1] = new
    x = torch.as_tensor(z, dtype=torch.float64, device=dev)
    lap = LapOp(w.to(dev), cfg.clustering.laplacian)
    opt = torch.optim.Adam(net.parameters(), lr=s.lr)
    t0 = time.time()
    steps = train_on(net, opt, x, lap, s, s.max_steps, s.tol, s.patience)
    fit_sec = time.time() - t0
    with torch.no_grad():
        yt = net(x)
        r = orthonorm_factor(yt, s.jitter)          # frozen for inference
        y = yt @ r
        mm = (y.T @ (lap @ y)) / y.shape[0]
        mm = 0.5 * (mm + mm.T)
        ritz, u = torch.linalg.eigh(mm)
        y_rot = y @ u
    return {"ritz": ritz.cpu().numpy(), "Y": y_rot.cpu().numpy(), "steps": steps, "fit_sec": fit_sec,
            "net": net, "R": r, "U": u, "warm": warm}


@torch.no_grad()
def transform(fit: dict, z_new: np.ndarray) -> np.ndarray:
    """Out-of-sample map of new segments with the frozen orthonormalisation and rotation."""
    net = fit["net"]
    dev = next(net.parameters()).device
    x = torch.as_tensor(z_new, dtype=torch.float64, device=dev)
    return (net(x) @ fit["R"] @ fit["U"]).cpu().numpy()
