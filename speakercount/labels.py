"""Overlap-aware segment labels (training and analysis only; never used at inference)."""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from .rttm import Turn
from .vad import merge_spans


def speaker_spans(turns: list[Turn]) -> dict[str, list[tuple[float, float]]]:
    by = defaultdict(list)
    for t in turns:
        by[t.speaker].append((t.start, t.end))
    return {spk: merge_spans(sp) for spk, sp in by.items()}


def _covered(spans: list[tuple[float, float]], starts: np.ndarray, ends: np.ndarray) -> np.ndarray:
    """Seconds of [start, end) covered by the (merged, sorted) spans, vectorised over windows."""
    out = np.zeros(len(starts))
    if not spans:
        return out
    arr = np.asarray(spans)
    for s, e in arr:  # per-speaker turn count is moderate; windows vectorised
        out += np.clip(np.minimum(ends, e) - np.maximum(starts, s), 0.0, None)
    return out


def segment_labels(turns: list[Turn], starts, ends, clean_main=0.9, clean_other=0.1):
    """Per window: clean label (or None), most-overlap label (or None), and speaker shares.

    clean: one speaker covers >= clean_main of the window AND every other <= clean_other.
    """
    starts, ends = np.asarray(starts, float), np.asarray(ends, float)
    spans = speaker_spans(turns)
    speakers = sorted(spans)
    width = np.maximum(ends - starts, 1e-9)
    if not speakers or len(starts) == 0:
        n = len(starts)
        return [None] * n, [None] * n, np.zeros((n, 0)), speakers
    shares = np.stack([_covered(spans[s], starts, ends) / width for s in speakers], axis=1)
    order = np.argsort(-shares, axis=1)
    top = shares[np.arange(len(starts)), order[:, 0]]
    second = shares[np.arange(len(starts)), order[:, 1]] if len(speakers) > 1 else np.zeros(len(starts))
    clean, most = [], []
    for i in range(len(starts)):
        best = speakers[order[i, 0]]
        clean.append(best if (top[i] >= clean_main - 1e-9 and second[i] <= clean_other + 1e-9) else None)
        most.append(best if top[i] > 0 else None)
    return clean, most, shares, speakers
