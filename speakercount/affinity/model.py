"""AffinityNet: session-level Transformer over ECAPA embeddings (replaces the Siamese network).

z = normalize(x + alpha * head(Transformer(Linear(x) + TimeEncoding(t))))
  * no activation on the output head (fixes old flaw 1: ReLU squeezing cosines >= 0)
  * residual over ECAPA, alpha init 0.1 -> starts close to raw ECAPA
  * affinity = cosine of z, used identically in training (loss), validation and inference
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class TimeEncoding(nn.Module):
    """Sinusoidal features of the segment centre time in seconds (periods 1 s .. 4000 s), projected."""

    def __init__(self, d_model: int, min_period: float = 1.0, max_period: float = 4000.0):
        super().__init__()
        n_freq = d_model // 2
        periods = torch.exp(torch.linspace(math.log(min_period), math.log(max_period), n_freq))
        self.register_buffer("omega", 2 * math.pi / periods, persistent=False)
        self.proj = nn.Linear(2 * n_freq, d_model)

    def forward(self, t: torch.Tensor) -> torch.Tensor:  # t: (B, N) seconds
        ang = t.float().unsqueeze(-1) * self.omega
        return self.proj(torch.cat([torch.sin(ang), torch.cos(ang)], dim=-1))


class AffinityNet(nn.Module):
    def __init__(self, in_dim=192, d_model=256, n_layers=4, n_heads=4, ffn=1024, dropout=0.1,
                 time_encoding=True, time_min_period=1.0, time_max_period=4000.0, alpha_init=0.1, **_):
        super().__init__()
        self.hparams = dict(in_dim=in_dim, d_model=d_model, n_layers=n_layers, n_heads=n_heads, ffn=ffn,
                            dropout=dropout, time_encoding=time_encoding, time_min_period=time_min_period,
                            time_max_period=time_max_period, alpha_init=alpha_init)
        self.inp = nn.Linear(in_dim, d_model)
        self.time = TimeEncoding(d_model, time_min_period, time_max_period) if time_encoding else None
        if n_layers > 0:
            layer = nn.TransformerEncoderLayer(d_model, n_heads, ffn, dropout, activation="gelu",
                                               batch_first=True, norm_first=True)
            self.encoder = nn.TransformerEncoder(layer, n_layers, enable_nested_tensor=False)
            self.ffn = None
        else:  # ablation: no context, per-segment residual MLP (a fixed "Siamese" branch)
            self.encoder = None
            self.ffn = nn.Sequential(nn.LayerNorm(d_model), nn.Linear(d_model, ffn), nn.GELU(),
                                     nn.Dropout(dropout), nn.Linear(ffn, d_model))
        self.norm = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, in_dim)  # linear: no activation
        # init so that ||head(h)|| ~ 1 (LayerNorm'd h has unit variance): z ~ raw ECAPA at start
        nn.init.normal_(self.head.weight, std=1.0 / math.sqrt(d_model * in_dim))
        nn.init.zeros_(self.head.bias)
        self.alpha = nn.Parameter(torch.tensor(float(alpha_init)))

    def forward(self, x: torch.Tensor, t: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        """x (B,N,D) L2-normalised ECAPA, t (B,N) seconds, mask (B,N) True = valid token."""
        h = self.inp(x)
        if self.time is not None:
            h = h + self.time(t)
        if self.encoder is not None:
            pad = None if mask is None else ~mask
            h = self.encoder(h, src_key_padding_mask=pad)
        else:
            h = h + self.ffn(h)
        delta = self.head(self.norm(h))
        z = x.float() + self.alpha.float() * delta.float()
        return F.normalize(z, dim=-1)
