"""Speech intervals: oracle (union of RTTM turns) or pyannote/segmentation-3.0."""

from __future__ import annotations

import os
from pathlib import Path

from .rttm import Turn


def merge_spans(spans: list[tuple[float, float]], merge_gap_sec: float = 0.0) -> list[tuple[float, float]]:
    spans = sorted((s, e) for s, e in spans if e > s)
    if not spans:
        return []
    merged = [list(spans[0])]
    for s, e in spans[1:]:
        if s - merged[-1][1] <= merge_gap_sec:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [(s, e) for s, e in merged]


def oracle_intervals(turns: list[Turn], duration: float | None = None, merge_gap_sec: float = 0.0):
    """Union of all speaker turns: overlapped speech collapses into one interval."""
    spans = []
    for t in turns:
        s, e = t.start, t.end
        if duration is not None:
            s, e = max(0.0, s), min(e, duration)
        spans.append((s, e))
    return merge_spans(spans, merge_gap_sec)


def total(intervals) -> float:
    return float(sum(e - s for s, e in intervals))


class PyannoteVad:
    """pyannote/segmentation-3.0 VAD (pyannote.audio 3.3.2 on torch 2.6)."""

    def __init__(self, vad_cfg):
        self.cfg = vad_cfg
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            import torch
            from huggingface_hub import hf_hub_download
            from pyannote.audio import Model
            from pyannote.audio.pipelines import VoiceActivityDetection

            token = os.environ.get("HF_TOKEN") or None
            # huggingface_hub>=1.0 dropped use_auth_token (still passed by pyannote 3.3.2):
            # download the checkpoint ourselves and load the local file.
            ckpt = hf_hub_download(self.cfg.model, "pytorch_model.bin", token=token)
            # torch 2.6 defaults to weights_only=True, which rejects this trusted checkpoint.
            original = torch.load

            def _load(*a, **k):
                k["weights_only"] = False
                return original(*a, **k)

            torch.load = _load
            try:
                model = Model.from_pretrained(ckpt)
            finally:
                torch.load = original
            pipe = VoiceActivityDetection(segmentation=model)
            pipe.instantiate({"min_duration_on": self.cfg.min_duration_on,
                              "min_duration_off": self.cfg.min_duration_off})
            dev = self.cfg.device if torch.cuda.is_available() else "cpu"
            self._pipeline = pipe.to(torch.device(dev))
        return self._pipeline

    def intervals(self, wav_path: str | Path) -> list[tuple[float, float]]:
        ann = self.pipeline(str(wav_path))
        return [(float(s.start), float(s.end)) for s in ann.get_timeline().support()]
