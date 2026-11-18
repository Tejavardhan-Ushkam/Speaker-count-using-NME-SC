"""Stage drivers: prepare (VAD + segment + embed + labels), cluster, evaluate, inspect."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .config import Cfg, work_dir
from .rttm import audio_path, list_recordings, read_rttm, rttm_path, speaker_count


# --------------------------------------------------------------------------- cache layout
def seg_file(cfg: Cfg, rec: str) -> Path:
    return work_dir(cfg) / "segments" / f"{rec}.json"


def emb_file(cfg: Cfg, rec: str) -> Path:
    return work_dir(cfg) / "embeddings" / f"{rec}.npy"


@dataclass
class Session:
    rec: str
    x: np.ndarray            # (N, 192) L2-normalised ECAPA
    start: np.ndarray
    end: np.ndarray
    center: np.ndarray
    interval: np.ndarray
    label: list              # clean speaker label or None
    label_most: list         # speaker with most overlap or None
    meta: dict

    @property
    def n(self) -> int:
        return int(self.x.shape[0])

    @property
    def ambiguous(self) -> np.ndarray:
        return np.array([lab is None for lab in self.label], dtype=bool)


def load_session(cfg: Cfg, rec: str) -> Session:
    d = json.loads(seg_file(cfg, rec).read_text())
    x = np.load(emb_file(cfg, rec))
    s = d["segments"]
    return Session(
        rec=rec, x=x,
        start=np.asarray(s["start"], float), end=np.asarray(s["end"], float),
        center=np.asarray(s["center"], float), interval=np.asarray(s["interval"], int),
        label=s["label"], label_most=s["label_most"], meta=d["meta"],
    )


def load_split(cfg: Cfg, only: list[str] | None = None) -> list[Session]:
    recs = list_recordings(cfg)
    if only:
        recs = [r for r in recs if r in set(only)]
    missing = [r for r in recs if not (seg_file(cfg, r).exists() and emb_file(cfg, r).exists())]
    if missing:
        raise FileNotFoundError(
            f"{len(missing)} recordings not prepared for {cfg.dataset.corpus}/{cfg.dataset.split} "
            f"(e.g. {missing[0]}); run `python run.py prepare --config ...` first"
        )
    return [load_session(cfg, r) for r in recs]


# --------------------------------------------------------------------------- prepare
def prepare(cfg: Cfg, force: bool = False, only: list[str] | None = None) -> None:
    from .config import write_run_metadata
    from .embedding import EcapaEmbedder, load_mono, probe_duration
    from .labels import segment_labels
    from .segmentation import segment_intervals
    from .vad import PyannoteVad, oracle_intervals, total

    recs = list_recordings(cfg)
    if only:
        recs = [r for r in recs if r in set(only)]
    wd = work_dir(cfg)
    write_run_metadata(cfg, wd)
    embedder = EcapaEmbedder(cfg.embedding)
    vad = PyannoteVad(cfg.vad) if cfg.vad.source == "pyannote" else None
    lab = cfg.labels
    t_all = time.time()
    n_seg_tot = n_amb_tot = 0
    for i, rec in enumerate(recs, 1):
        if not force and seg_file(cfg, rec).exists() and emb_file(cfg, rec).exists():
            meta = json.loads(seg_file(cfg, rec).read_text())["meta"]
            n_seg_tot += meta["n_segments"]
            n_amb_tot += meta["n_ambiguous"]
            continue
        t0 = time.time()
        turns = read_rttm(rttm_path(cfg, rec))
        wav_path = audio_path(cfg, rec)
        duration = probe_duration(wav_path)
        t_vad = time.time()
        if vad is None:
            intervals = oracle_intervals(turns, duration, cfg.segmentation.merge_gap_sec)
        else:
            intervals = vad.intervals(wav_path)
        t_vad = time.time() - t_vad
        segs = segment_intervals(intervals, cfg.segmentation)
        starts = np.array([s.start for s in segs])
        ends = np.array([s.end for s in segs])
        clean, most, shares, _ = segment_labels(turns, starts, ends, lab.clean_main_share, lab.clean_other_share)
        t_emb = time.time()
        wav = load_mono(wav_path, cfg.embedding.sample_rate)
        x = embedder.encode(wav, starts, cfg.segmentation.window_sec)
        t_emb = time.time() - t_emb
        n_amb = int(sum(c is None for c in clean))
        meta = {
            "recording_id": rec,
            "k_true": speaker_count(turns),
            "duration_sec": duration,
            "speech_sec": total(intervals),
            "ref_speech_sec": total(oracle_intervals(turns, duration)),
            "n_intervals": len(intervals),
            "n_segments": len(segs),
            "n_ambiguous": n_amb,
            "vad_source": cfg.vad.source,
            "time_vad_sec": t_vad,
            "time_embed_sec": t_emb,
        }
        payload = {
            "meta": meta,
            "segments": {
                "start": starts.round(4).tolist(),
                "end": ends.round(4).tolist(),
                "center": ((starts + ends) / 2).round(4).tolist(),
                "interval": [s.interval_index for s in segs],
                "label": clean,
                "label_most": most,
                "max_share": (shares.max(axis=1) if shares.size else np.zeros(len(segs))).round(4).tolist(),
            },
        }
        emb_file(cfg, rec).parent.mkdir(parents=True, exist_ok=True)
        seg_file(cfg, rec).parent.mkdir(parents=True, exist_ok=True)
        np.save(emb_file(cfg, rec), x)
        seg_file(cfg, rec).write_text(json.dumps(payload))
        n_seg_tot += len(segs)
        n_amb_tot += n_amb
        print(f"[prepare {cfg.dataset.corpus}/{cfg.dataset.split}] {i}/{len(recs)} {rec}: "
              f"N={len(segs)} ambiguous={n_amb} K={meta['k_true']} "
              f"({time.time() - t0:.1f} s)", flush=True)
    frac = n_amb_tot / max(1, n_seg_tot)
    print(f"[prepare {cfg.dataset.corpus}/{cfg.dataset.split}] {len(recs)} recordings, "
          f"{n_seg_tot} segments, {n_amb_tot} ambiguous ({100 * frac:.1f} %), "
          f"{time.time() - t_all:.1f} s")


# --------------------------------------------------------------------------- later phases
def cluster_split(cfg: Cfg, only=None, force: bool = False):
    from .cluster.run import cluster_split as _cs

    return _cs(cfg, only=only, force=force)


def evaluate(cfg: Cfg, force: bool = False):
    from .eval.evaluate import evaluate as _ev

    return _ev(cfg, force=force)


def inspect(cfg: Cfg, rec: str):
    from .eval.evaluate import inspect as _in

    return _in(cfg, rec)
