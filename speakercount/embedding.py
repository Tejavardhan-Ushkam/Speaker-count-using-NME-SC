"""Audio loading and SpeechBrain ECAPA embeddings (one L2-normalised 192-d vector per segment)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import torch

from .config import resolve_path


def resolve_device(requested: str) -> str:
    if requested == "cuda" and not torch.cuda.is_available():
        return "cpu"
    return requested


def load_mono(p: str | Path, target_sr: int) -> np.ndarray:
    import soundfile as sf

    wav, sr = sf.read(str(p), dtype="float32", always_2d=True)
    wav = wav.mean(axis=1)
    if sr != target_sr:
        import torchaudio.functional as AF

        wav = AF.resample(torch.from_numpy(wav), sr, target_sr).numpy()
    return np.ascontiguousarray(wav, dtype=np.float32)


def probe_duration(p: str | Path) -> float:
    import soundfile as sf

    info = sf.info(str(p))
    return info.frames / info.samplerate


class EcapaEmbedder:
    def __init__(self, emb_cfg):
        self.cfg = emb_cfg
        self.device = resolve_device(emb_cfg.device)
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from speechbrain.inference.speaker import EncoderClassifier

            self._model = EncoderClassifier.from_hparams(
                source=self.cfg.model,
                savedir=str(resolve_path(self.cfg.savedir)),
                run_opts={"device": self.device},
            )
            self._model.eval()
        return self._model

    def encode(self, wav: np.ndarray, starts: np.ndarray, window_sec: float) -> np.ndarray:
        try:
            return self._encode(wav, starts, window_sec)
        except torch.cuda.OutOfMemoryError:  # shared GPU full: reload ECAPA on CPU and redo
            torch.cuda.empty_cache()
            print("[ecapa] GPU out of memory: embedding moved to CPU")
            self.device, self._model = "cpu", None
            return self._encode(wav, starts, window_sec)

    @torch.inference_mode()
    def _encode(self, wav: np.ndarray, starts: np.ndarray, window_sec: float) -> np.ndarray:
        sr = self.cfg.sample_rate
        n_samp = int(round(window_sec * sr))
        if len(starts) == 0:
            return np.zeros((0, self.cfg.dim), dtype=np.float32)
        w = torch.from_numpy(wav)
        if w.numel() < n_samp:
            w = torch.nn.functional.pad(w, (0, n_samp - w.numel()))
        offs = np.clip(np.rint(np.asarray(starts) * sr).astype(np.int64), 0, max(0, w.numel() - n_samp))
        out = np.empty((len(starts), self.cfg.dim), dtype=np.float32)
        bs = self.cfg.batch_size
        lengths = torch.ones(bs, device=self.device)
        for lo in range(0, len(starts), bs):
            chunk = offs[lo:lo + bs]
            frames = torch.stack([w[o:o + n_samp] for o in chunk]).to(self.device)
            e = self.model.encode_batch(frames, lengths[: len(chunk)]).squeeze(1)
            out[lo:lo + len(chunk)] = torch.nn.functional.normalize(e.float(), dim=-1).cpu().numpy()
        return out
