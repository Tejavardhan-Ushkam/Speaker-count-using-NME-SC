"""1.5 s / 0.75 s windows inside each speech interval, never crossing silence (old rules)."""

from __future__ import annotations

import math
from dataclasses import dataclass

_TOL = 1e-9


@dataclass(frozen=True)
class Segment:
    start: float
    end: float
    interval_index: int

    @property
    def center(self) -> float:
        return 0.5 * (self.start + self.end)


def segment_intervals(intervals: list[tuple[float, float]], seg_cfg) -> list[Segment]:
    window, hop = seg_cfg.window_sec, seg_cfg.hop_sec
    out: list[Segment] = []
    for idx, (start, end) in enumerate(intervals):
        span = end - start
        if span + _TOL < seg_cfg.min_interval_sec:  # intervals shorter than the window are dropped
            continue
        n = int(math.floor((span - window) / hop + _TOL)) + 1
        if n < 1:
            continue
        if n == 1 and seg_cfg.center_single_window:  # single window is centred in its interval
            off = 0.5 * (span - window)
            out.append(Segment(start + off, start + off + window, idx))
            continue
        for i in range(n):
            s = start + i * hop
            out.append(Segment(s, s + window, idx))
    return out
