"""Hypothesis RTTM from segment labels, and DER with pyannote.metrics.

Collar: the prompt's "collar 0.25 s" is the usual md-eval convention (+-0.25 s around every
reference boundary). pyannote.metrics' `collar` is the *total* width, so we pass 2 * 0.25 = 0.5.
"""

from __future__ import annotations

import numpy as np

from ..rttm import Turn


def hyp_turns(rec: str, start: np.ndarray, end: np.ndarray, labels: np.ndarray, step: float = 0.01) -> list[Turn]:
    """Each frame inside some segment gets the label of the segment whose centre is nearest;
    consecutive equal labels are merged."""
    if len(start) == 0:
        return []
    centers = 0.5 * (start + end)
    t_end = float(end.max())
    frames = np.arange(0.0, t_end, step) + step / 2
    # covered frames: inside the union of segments
    order = np.argsort(start)
    s_sorted, e_sorted = start[order], end[order]
    run_max_end = np.maximum.accumulate(e_sorted)
    idx = np.searchsorted(s_sorted, frames, side="right") - 1
    covered = (idx >= 0) & (run_max_end[np.clip(idx, 0, None)] > frames)
    # nearest centre (centres are sorted in time order)
    c_order = np.argsort(centers)
    c_sorted = centers[c_order]
    j = np.clip(np.searchsorted(c_sorted, frames), 1, len(c_sorted) - 1) if len(c_sorted) > 1 else np.zeros(len(frames), int)
    if len(c_sorted) > 1:
        left_closer = np.abs(frames - c_sorted[j - 1]) <= np.abs(c_sorted[j] - frames)
        j = np.where(left_closer, j - 1, j)
    lab = labels[c_order[j]]
    turns: list[Turn] = []
    cur_lab, cur_s, prev_f = None, None, None
    for f, ok, l in zip(frames, covered, lab):
        if ok and cur_lab == l and prev_f is not None and abs(f - prev_f - step) < step / 2:
            prev_f = f
            continue
        if cur_lab is not None:
            turns.append(Turn(rec, cur_s, prev_f + step / 2 - cur_s, f"spk{int(cur_lab):02d}"))
        if ok:
            cur_lab, cur_s, prev_f = l, f - step / 2, f
        else:
            cur_lab, cur_s, prev_f = None, None, None
    if cur_lab is not None:
        turns.append(Turn(rec, cur_s, prev_f + step / 2 - cur_s, f"spk{int(cur_lab):02d}"))
    return turns


def _annotation(turns: list[Turn]):
    from pyannote.core import Annotation, Segment

    ann = Annotation()
    for i, t in enumerate(turns):
        ann[Segment(t.start, t.end), i] = t.speaker
    return ann


def der(ref: list[Turn], hyp: list[Turn], collar: float = 0.25, skip_overlap: bool = False) -> dict:
    from pyannote.metrics.diarization import DiarizationErrorRate

    metric = DiarizationErrorRate(collar=2 * collar, skip_overlap=skip_overlap)
    comp = metric(_annotation(ref), _annotation(hyp), detailed=True)
    total = comp["total"]
    return {
        "der": float(comp["diarization error rate"]),
        "miss": float(comp["missed detection"] / total) if total else 0.0,
        "fa": float(comp["false alarm"] / total) if total else 0.0,
        "conf": float(comp["confusion"] / total) if total else 0.0,
    }
