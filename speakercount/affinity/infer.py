"""AffinityNet inference: one full-session forward pass, or overlapping chunks if too long / OOM."""

from __future__ import annotations

import numpy as np
import torch

from ..config import resolve_path
from ..embedding import resolve_device
from .model import AffinityNet


def load_affnet(path, device: str = "cuda") -> AffinityNet:
    ck = torch.load(resolve_path(path), map_location="cpu", weights_only=False)
    model = AffinityNet(**ck["hparams"])
    model.load_state_dict(ck["model"])
    return model.to(resolve_device(device)).eval()


@torch.no_grad()
def embed_full(model: AffinityNet, x: np.ndarray, t: np.ndarray) -> np.ndarray:
    dev = next(model.parameters()).device
    xt = torch.as_tensor(x, dtype=torch.float32, device=dev)[None]
    tt = torch.as_tensor(t, dtype=torch.float32, device=dev)[None]
    with torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=dev.type == "cuda"):
        z = model(xt, tt)
    return z[0].float().cpu().numpy()


@torch.no_grad()
def embed_chunked(model: AffinityNet, x: np.ndarray, t: np.ndarray, chunk: int = 2048, stride: int = 1024) -> np.ndarray:
    n = len(x)
    acc = np.zeros((n, x.shape[1]), dtype=np.float64)
    cnt = np.zeros(n)
    starts = list(range(0, max(1, n - chunk) + 1, stride))
    if starts[-1] + chunk < n:
        starts.append(n - chunk)
    for s in starts:
        e = min(n, s + chunk)
        acc[s:e] += embed_full(model, x[s:e], t[s:e])
        cnt[s:e] += 1
    z = acc / cnt[:, None]
    return (z / np.maximum(np.linalg.norm(z, axis=1, keepdims=True), 1e-12)).astype(np.float32)


def embed(model: AffinityNet, x, t, max_full: int = 6000, chunk: int = 2048, stride: int = 1024) -> np.ndarray:
    if len(x) <= max_full:
        try:
            return embed_full(model, x, t)
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
    return embed_chunked(model, x, t, chunk, stride)


class AffnetInference:
    def __init__(self, cfg):
        self.cfg = cfg
        self.model = load_affnet(cfg.affinity.checkpoint, cfg.affnet.device)

    def __call__(self, x: np.ndarray, t: np.ndarray) -> np.ndarray:
        a = self.cfg.affinity
        try:
            return embed(self.model, x, t, a.infer_max_full, a.infer_chunk, a.infer_stride)
        except torch.cuda.OutOfMemoryError:  # shared GPU full: continue on CPU
            torch.cuda.empty_cache()
            print("[affnet] GPU out of memory: inference moved to CPU")
            self.model = self.model.cpu()
            return embed(self.model, x, t, a.infer_max_full, a.infer_chunk, a.infer_stride)
