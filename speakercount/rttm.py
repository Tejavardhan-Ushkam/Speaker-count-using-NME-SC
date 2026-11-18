"""RTTM I/O, recording listing and reference speaker counts."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .config import Cfg, resolve_path


@dataclass(frozen=True)
class Turn:
    recording_id: str
    start: float
    duration: float
    speaker: str

    @property
    def end(self) -> float:
        return self.start + self.duration


def read_rttm(p: str | Path) -> list[Turn]:
    turns: list[Turn] = []
    for lineno, line in enumerate(Path(p).read_text().splitlines(), 1):
        f = line.split()
        if not f or f[0] != "SPEAKER":
            continue
        if len(f) < 8:
            raise ValueError(f"{p}:{lineno}: malformed SPEAKER line")
        turns.append(Turn(f[1], float(f[3]), float(f[4]), f[7]))
    return turns


def write_rttm(p: str | Path, turns: list[Turn]) -> None:
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"SPEAKER {t.recording_id} 1 {t.start:.3f} {t.duration:.3f} <NA> <NA> {t.speaker} <NA> <NA>"
        for t in turns
    ]
    p.write_text("\n".join(lines) + ("\n" if lines else ""))


def speaker_count(turns: list[Turn]) -> int:
    """K_true = number of distinct speakers in the RTTM."""
    return len({t.speaker for t in turns})


def rttm_path(cfg: Cfg, rec: str) -> Path:
    return resolve_path(cfg.dataset.rttm_dir) / f"{rec}.rttm"


def audio_path(cfg: Cfg, rec: str) -> Path:
    return resolve_path(cfg.dataset.audio_dir) / cfg.dataset.audio_template.format(rec=rec)


def list_recordings(cfg: Cfg) -> list[str]:
    """Recording ids of this split: RTTMs in rttm_dir, restricted to recordings_file if given."""
    rttm_dir = resolve_path(cfg.dataset.rttm_dir)
    recs = sorted(p.stem for p in rttm_dir.glob("*.rttm"))
    if cfg.dataset.recordings_file:
        f = resolve_path(cfg.dataset.recordings_file)
        if not f.exists():
            raise FileNotFoundError(f"{f} missing: run `python run.py make-splits` first")
        keep = [r.strip() for r in f.read_text().splitlines() if r.strip()]
        missing = sorted(set(keep) - set(recs))
        if missing:
            raise FileNotFoundError(f"recordings in {f} without RTTM: {missing[:5]}")
        recs = sorted(keep)
    return recs


def reference_counts(cfg: Cfg) -> dict[str, int]:
    return {r: speaker_count(read_rttm(rttm_path(cfg, r))) for r in list_recordings(cfg)}


def mode_k(cfg: Cfg) -> int:
    """Most common K of the training split for this corpus (ties -> smaller K)."""
    from .config import load_config

    train = load_config(cfg.dataset.train_config)
    counts = Counter(reference_counts(train).values())
    best = max(counts.values())
    return min(k for k, c in counts.items() if c == best)
