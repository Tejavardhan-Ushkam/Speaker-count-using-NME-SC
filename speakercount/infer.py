"""Count speakers in one arbitrary audio file (no reference RTTM): the deployment entry point.

audio (any format ffmpeg reads) -> 16 kHz mono wav -> pyannote VAD -> 1.5 s / 0.75 s windows
-> ECAPA -> NME-SC graph -> SpectralNet / exact eigh -> post-processing (tuned values) -> K.

    from speakercount.infer import SpeakerCounter
    counter = SpeakerCounter("deploy/model.yaml")
    result = counter.predict("meeting.mp3")      # JSON-serialisable dict

CLI:  python run.py predict --audio file.wav [--model deploy/model.yaml]
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

import numpy as np
import yaml

from .config import ROOT, git_commit, load_config, resolve_path

DEFAULT_MODEL = "deploy/model.yaml"


def to_wav16k(src: str | Path, dst: str | Path) -> None:
    """Decode anything ffmpeg understands (wav, mp3, m4a, flac, ogg, webm, mp4 ...) to 16 kHz mono PCM wav."""
    ff = shutil.which("ffmpeg")
    if ff is None:  # fall back to soundfile (wav / flac / ogg / mp3 only)
        import soundfile as sf

        from .embedding import load_mono

        sf.write(str(dst), load_mono(src, 16000), 16000, subtype="PCM_16")
        return
    r = subprocess.run([ff, "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
                        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(dst)], capture_output=True, text=True)
    if r.returncode != 0:
        raise ValueError(f"could not decode audio: {r.stderr.strip()[:300]}")


def _turns(starts, ends, intervals, labels, hop):
    """Speaker turns from overlapping windows: each window owns its central hop-long part; the first and
    last window of a speech interval also own the interval's edges."""
    out = []
    n = len(starts)
    for i, (s, e, iv, lab) in enumerate(zip(starts, ends, intervals, labels)):
        c = 0.5 * (s + e)
        a, b = max(iv[0], c - hop / 2), min(iv[1], c + hop / 2)
        if i == 0 or intervals[i - 1] != iv:
            a = iv[0]
        if i == n - 1 or intervals[i + 1] != iv:
            b = iv[1]
        if out and out[-1]["speaker"] == lab and a - out[-1]["end"] < 1e-3:
            out[-1]["end"] = round(float(b), 2)
        else:
            out.append({"speaker": int(lab), "start": round(float(a), 2), "end": round(float(b), 2)})
    return out


class SpeakerCounter:
    def __init__(self, model_yaml: str | Path = DEFAULT_MODEL, device: str | None = None):
        spec = yaml.safe_load(resolve_path(model_yaml).read_text())
        self.spec = spec
        dev = device or os.environ.get("SPEAKERCOUNT_DEVICE") or spec.get("device", "cpu")
        over = {"vad": {"source": "pyannote", "device": dev}, "embedding": {"device": dev},
                "clustering": {"device": dev}, "spectralnet": {"device": dev, "warm_start": False},
                "postprocess": {"tuned_file": spec["tuned_file"]}}
        self.cfg = load_config(None, method=spec["method"], overrides=over)
        from .cluster.run import tuned_postprocess

        self.pp = tuned_postprocess(self.cfg)
        if self.pp.get("p_min") is not None:
            self.cfg.clustering.p_min = int(self.pp["p_min"])
        if self.pp.get("k_max") is not None:
            self.cfg.clustering.k_max = int(self.pp["k_max"])
        elif spec.get("k_max"):
            self.cfg.clustering.k_max = int(spec["k_max"])
        from .embedding import EcapaEmbedder
        from .vad import PyannoteVad

        self.vad = PyannoteVad(self.cfg.vad)
        self.ecapa = EcapaEmbedder(self.cfg.embedding)
        self.version = spec.get("version") or git_commit()

    def warmup(self) -> None:
        """Load both networks (first request is otherwise slow)."""
        _ = self.vad.pipeline, self.ecapa.model

    def info(self) -> dict:
        c = self.cfg.clustering
        return {"name": self.spec.get("display_name", self.spec["method"]), "method": self.spec["method"],
                "version": self.version, "k_max": int(c.k_max), "p_min": int(c.p_min),
                "postprocess": {k: self.pp[k] for k in ("min_cluster_share", "share_mode", "merge_threshold",
                                                        "single_speaker_threshold")},
                "measured_accuracy": self.spec.get("measured_accuracy", {}),
                "scope": self.spec.get("scope", "")}

    def predict(self, audio: str | Path, max_sec: float | None = None) -> dict:
        from .cluster.run import cluster_session
        from .embedding import load_mono
        from .pipeline import Session
        from .segmentation import segment_intervals
        from .vad import total

        t0 = time.time()
        cfg = self.cfg
        with tempfile.TemporaryDirectory() as tmp:
            wav_path = Path(tmp) / "audio.wav"
            to_wav16k(audio, wav_path)
            wav = load_mono(wav_path, cfg.embedding.sample_rate)
            duration = len(wav) / cfg.embedding.sample_rate
            if max_sec and duration > max_sec:
                raise ValueError(f"audio is {duration / 60:.1f} min; the limit is {max_sec / 60:.0f} min")
            t = time.time()
            intervals = self.vad.intervals(wav_path)
            t_vad = time.time() - t
        segs = segment_intervals(intervals, cfg.segmentation)
        base = {"model": self.info(), "audio": {"duration_sec": round(duration, 2),
                                                "speech_sec": round(total(intervals), 2)}}
        notes = []
        if not segs:
            notes.append("No speech of at least 1.5 s was detected, so no speaker could be counted.")
            return base | {"num_speakers": 0, "speakers": [], "turns": [], "notes": notes,
                           "diagnostics": {"n_segments": 0}, "processing_sec": round(time.time() - t0, 2)}
        starts = np.array([s.start for s in segs])
        ends = np.array([s.end for s in segs])
        t = time.time()
        x = self.ecapa.encode(wav, starts, cfg.segmentation.window_sec)
        t_emb = time.time() - t
        n = len(segs)
        sess = Session(rec="upload", x=x, start=starts, end=ends, center=(starts + ends) / 2,
                       interval=np.array([s.interval_index for s in segs]), label=["?"] * n, label_most=["?"] * n,
                       meta={"k_true": None})
        res = cluster_session(sess, x, cfg, self.pp)
        labels = np.asarray(res["labels"])
        # speaker ids 1..K ordered by first appearance
        order = {lab: i + 1 for i, lab in enumerate(dict.fromkeys(labels.tolist()))}
        lab1 = np.array([order[v] for v in labels.tolist()])
        iv = [intervals[s.interval_index] for s in segs]
        turns = _turns(starts, ends, iv, lab1, cfg.segmentation.hop_sec)
        talk = {}
        for tr in turns:
            talk[tr["speaker"]] = talk.get(tr["speaker"], 0.0) + tr["end"] - tr["start"]
        tot = sum(talk.values()) or 1.0
        speakers = [{"id": k, "label": f"Speaker {k}", "talk_time_sec": round(v, 2), "share": round(v / tot, 4)}
                    for k, v in sorted(talk.items())]
        k = int(res["k_pred"])
        if k >= cfg.clustering.k_max:
            notes.append(f"The count reached the model's upper limit ({cfg.clustering.k_max}); "
                         "the recording may contain more speakers than the model supports.")
        if total(intervals) < 30:
            notes.append("Less than 30 s of speech was detected; counts on very short audio are less reliable.")
        ev = np.asarray(res.get("eigenvalues", []), float)
        return base | {
            "num_speakers": k,
            "speakers": speakers,
            "turns": turns,
            "notes": notes,
            "diagnostics": {"n_segments": n, "k_before_postprocessing": int(res.get("k_eigengap", k)),
                            "p_star": int(res.get("p_star", 0)), "gap_ratio": (lambda g: round(g, 3) if np.isfinite(g) else None)(float(res.get("gap_ratio", 0) or 0)),
                            "eigenvalues": [round(float(v), 5) for v in ev[: min(len(ev), 12)]],
                            "time_vad_sec": round(t_vad, 2), "time_embed_sec": round(t_emb, 2),
                            "time_cluster_sec": round(float(res["time_cluster_sec"]), 2)},
            "processing_sec": round(time.time() - t0, 2),
        }


def main_predict(audio: str, model: str = DEFAULT_MODEL) -> dict:
    return SpeakerCounter(model).predict(audio)


__all__ = ["SpeakerCounter", "to_wav16k", "main_predict", "ROOT"]
