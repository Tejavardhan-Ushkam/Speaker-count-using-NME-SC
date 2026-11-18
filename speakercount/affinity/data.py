"""Chunk sampler for AffinityNet training (prompt §4.3)."""

from __future__ import annotations

import numpy as np
import torch

from ..pipeline import Session


class ChunkSampler:
    def __init__(self, corpora: dict[str, list[Session]], a, seed: int = 0):
        """corpora: corpus name -> training sessions; a: cfg.affnet."""
        self.corpora = {k: v for k, v in corpora.items() if v}
        self.a = a
        self.rng = np.random.default_rng(seed)
        self.names = sorted(self.corpora)

    def n_sessions(self) -> int:
        return sum(len(v) for v in self.corpora.values())

    def _pick_corpus(self) -> str:
        if self.a.corpus_balance and len(self.names) > 1:
            return self.names[int(self.rng.integers(len(self.names)))]  # 50/50
        sizes = np.array([len(self.corpora[n]) for n in self.names], float)
        return self.names[int(self.rng.choice(len(self.names), p=sizes / sizes.sum()))]

    def _chunk(self, s: Session, prefix: str = ""):
        a, rng = self.a, self.rng
        L = int(rng.integers(a.chunk_min, a.chunk_max + 1))
        lo = 0 if s.n <= L else int(rng.integers(0, s.n - L + 1))
        idx = np.arange(lo, min(s.n, lo + L))
        labels_src = s.label_most if a.get("label_mode", "clean") == "most_overlap" else s.label
        lab = [labels_src[i] for i in idx]
        owner = [s.label_most[i] for i in idx]  # who a segment "belongs to", for speaker dropout
        if a.speaker_dropout > 0 and rng.random() < a.speaker_dropout:
            spk = sorted({o for o in owner if o is not None})
            if len(spk) > 1:
                n_drop = int(rng.integers(1, len(spk)))       # keep at least one speaker
                drop = set(rng.choice(spk, size=n_drop, replace=False).tolist())
                keep = np.array([o not in drop for o in owner])
                idx = idx[keep]
                lab = [l for l, k in zip(lab, keep) if k]
        if a.segment_dropout > 0 and len(idx) > 8:
            keep = rng.random(len(idx)) >= a.segment_dropout
            idx = idx[keep]
            lab = [l for l, k in zip(lab, keep) if k]
        x = s.x[idx].astype(np.float32)
        if a.emb_noise > 0:
            x = x + a.emb_noise * rng.standard_normal(x.shape).astype(np.float32)
            x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-12)
        t = s.center[idx].astype(np.float32)
        lab = [None if l is None else f"{prefix}{l}" for l in lab]
        return x, t, lab

    def sample_chunk(self):
        corpus = self._pick_corpus()
        sess = self.corpora[corpus]
        s = sess[int(self.rng.integers(len(sess)))]
        x, t, lab = self._chunk(s)
        if self.a.session_mixing and len(sess) > 1:  # ablation: 2 sessions of the same corpus
            s2 = sess[int(self.rng.integers(len(sess)))]
            if s2.rec != s.rec:
                x2, t2, lab2 = self._chunk(s2, prefix="B:")
                x = np.concatenate([x, x2])
                t = np.concatenate([t, t2 + (t.max() if len(t) else 0.0) + 5.0])
                lab = lab + lab2
        return x, t, lab

    def batch(self, n_chunks: int):
        chunks = [self.sample_chunk() for _ in range(n_chunks)]
        return collate(chunks)


def collate(chunks):
    """Pad to the longest chunk. labels: per-chunk int ids, -1 for ambiguous and padding."""
    n_max = max(len(c[0]) for c in chunks)
    d = chunks[0][0].shape[1]
    B = len(chunks)
    x = torch.zeros(B, n_max, d)
    t = torch.zeros(B, n_max)
    mask = torch.zeros(B, n_max, dtype=torch.bool)
    labels = torch.full((B, n_max), -1, dtype=torch.long)
    for b, (xc, tc, lc) in enumerate(chunks):
        n = len(xc)
        x[b, :n] = torch.from_numpy(xc)
        t[b, :n] = torch.from_numpy(tc)
        mask[b, :n] = True
        ids = {}
        for i, l in enumerate(lc):
            if l is not None:
                labels[b, i] = ids.setdefault(l, len(ids))
    return x, t, mask, labels
