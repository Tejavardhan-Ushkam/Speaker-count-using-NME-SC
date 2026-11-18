"""Pairwise logistic loss on all clean pairs + supervised contrastive loss, both on cosine of z.

labels: (B, N) int, >= 0 clean speaker id (within the chunk), -1 = ambiguous or padding
(ambiguous tokens are context for attention but are masked out of the loss).
"""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class AffinityLoss(nn.Module):
    def __init__(self, w_init=10.0, b_init=-5.0, bce_weight=1.0, supcon_weight=0.5, temperature=0.1):
        super().__init__()
        self.w_raw = nn.Parameter(torch.tensor(math.log(math.expm1(w_init))))  # softplus^-1
        self.b = nn.Parameter(torch.tensor(float(b_init)))
        self.bce_weight, self.supcon_weight, self.temperature = bce_weight, supcon_weight, temperature

    def forward(self, z: torch.Tensor, labels: torch.Tensor) -> dict:
        bce_terms, sc_terms = [], []
        w = F.softplus(self.w_raw)
        for zb, lb in zip(z, labels):
            keep = lb >= 0
            if keep.sum() < 2:
                continue
            zc, lc = zb[keep].float(), lb[keep]
            cos = zc @ zc.T
            same = (lc[:, None] == lc[None, :]).float()
            n = zc.shape[0]
            iu = torch.triu_indices(n, n, offset=1, device=zc.device)
            s, y = w * cos[iu[0], iu[1]] + self.b, same[iu[0], iu[1]]
            n_pos = y.sum()
            n_neg = y.numel() - n_pos
            if self.bce_weight > 0 and n_pos > 0:
                pw = (n_neg / n_pos.clamp_min(1)).detach()
                bce_terms.append(F.binary_cross_entropy_with_logits(s, y, pos_weight=pw))
            elif self.bce_weight > 0:
                bce_terms.append(F.binary_cross_entropy_with_logits(s, y))
            if self.supcon_weight > 0:
                logits = cos / self.temperature
                eye = torch.eye(n, dtype=torch.bool, device=zc.device)
                logits = logits.masked_fill(eye, -1e9)
                log_prob = logits - torch.logsumexp(logits, dim=1, keepdim=True)
                pos = same.bool() & ~eye
                n_p = pos.sum(1)
                ok = n_p > 0
                if ok.any():
                    mean_lp = (log_prob * pos).sum(1)[ok] / n_p[ok]
                    sc_terms.append(-mean_lp.mean())
        zero = z.sum() * 0.0
        bce = torch.stack(bce_terms).mean() if bce_terms else zero
        sc = torch.stack(sc_terms).mean() if sc_terms else zero
        total = self.bce_weight * bce + self.supcon_weight * sc
        return {"loss": total, "bce": bce.detach(), "supcon": sc.detach()}
