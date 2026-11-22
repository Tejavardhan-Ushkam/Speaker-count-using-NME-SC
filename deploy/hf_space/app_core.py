"""Analysis logic for the Space, kept free of gradio/spaces imports so it can be tested anywhere.

Models are loaded on CPU at start-up. For each request, `analyse` moves them to the GPU when one is available
(ZeroGPU attaches a GPU only inside @spaces.GPU functions) and back to CPU afterwards.
"""

from __future__ import annotations

import os

# secrets pasted into the Space settings often carry a trailing newline, which HTTP headers reject
if os.environ.get("HF_TOKEN"):
    os.environ["HF_TOKEN"] = os.environ["HF_TOKEN"].strip()

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import torch  # noqa: E402

from speakercount.infer import SpeakerCounter  # noqa: E402

MAX_SEC = float(os.environ.get("MAX_AUDIO_SEC", "1800"))
COLORS = ["#4f46e5", "#e11d48", "#059669", "#d97706", "#0891b2", "#7c3aed", "#db2777", "#65a30d", "#2563eb",
          "#ea580c", "#0d9488", "#9333ea"]

COUNTER = SpeakerCounter("deploy/model.yaml", device="cpu")
COUNTER.warmup()


def _move(dev: str) -> None:
    c = COUNTER
    c.cfg.clustering.device = dev
    c.ecapa.device = dev
    m = c.ecapa.model
    m.mods.to(dev)
    m.device = dev
    c.vad.pipeline.to(torch.device(dev))


def analyse(path: str) -> dict:
    """Count speakers in one file (call this from inside the @spaces.GPU function)."""
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        if dev == "cuda":
            _move("cuda")
        r = COUNTER.predict(path, max_sec=MAX_SEC)
        r["device"] = dev
        return r
    finally:
        if dev == "cuda":
            _move("cpu")


def fmt(s: float) -> str:
    s = max(0.0, float(s))
    return f"{int(s // 60)}:{int(s % 60):02d}"


def summary_md(r: dict) -> str:
    k = r["num_speakers"]
    head = "## No speech detected" if k == 0 else f"# {k} speaker{'s' if k != 1 else ''} detected"
    a = r.get("audio", {})
    lines = [head, "",
             f"**Audio length** {fmt(a.get('duration_sec', 0))} · **speech detected** {fmt(a.get('speech_sec', 0))} · "
             f"**processing** {r.get('processing_sec', '–')} s"]
    for n in r.get("notes", []):
        lines += ["", f"> ⚠️ {n}"]
    if r.get("speakers"):
        lines += ["", "| Speaker | Talk time | Share |", "|---|---|---|"]
        lines += [f"| {s['label']} | {fmt(s['talk_time_sec'])} | {round(100 * s['share'])} % |" for s in r["speakers"]]
    return "\n".join(lines)


def timeline_fig(r: dict):
    sp, tr = r.get("speakers", []), r.get("turns", [])
    dur = max(1.0, r.get("audio", {}).get("duration_sec", 1.0))
    fig, ax = plt.subplots(figsize=(9, 0.55 * max(1, len(sp)) + 1.1))
    for row, s in enumerate(sp):
        bars = [(t["start"], t["end"] - t["start"]) for t in tr if t["speaker"] == s["id"]]
        ax.broken_barh(bars, (row - 0.35, 0.7), color=COLORS[(s["id"] - 1) % len(COLORS)])
    ax.set_yticks(range(len(sp)), [s["label"] for s in sp])
    ax.set_ylim(-0.6, max(0, len(sp) - 1) + 0.6)
    ax.invert_yaxis()
    ax.set_xlim(0, dur)
    ticks = [dur * i / 6 for i in range(7)]
    ax.set_xticks(ticks, [fmt(t) for t in ticks])
    ax.set_xlabel("time (min:s)")
    ax.set_title("Who spoke when")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    fig.tight_layout()
    return fig


def about_md() -> str:
    m = COUNTER.info()
    rows = "\n".join(f"| {k} | {round(100 * v['exact'])} % | {round(100 * v['within_1'])} % | {v['mae']} |"
                     for k, v in m.get("measured_accuracy", {}).items())
    return f"""**Model:** {m['name']} · version `{m['version']}` · max speakers {m['k_max']} · p_min {m['p_min']}

1. **Speech detection** (pyannote) finds where someone is talking.
2. Speech is cut into overlapping **1.5 s windows**.
3. Each window becomes a 192-number **voice fingerprint** (ECAPA-TDNN speaker embedding).
4. Windows are linked to their most similar neighbours in a graph, and **NME-SC spectral clustering** groups them. The number of groups
   is read from the largest jump in the graph's eigenvalues (the eigengap).
5. The groups are the speakers; their windows give the timeline.

**Measured accuracy** on held-out test sets, with the same automatic speech detection as this page:

| Test set | Exact count | Within ±1 | Mean abs. error |
|---|---|---|---|
{rows}

{m.get('scope', '')}

*Research prototype. Audio is processed only for this request and is not stored. Do not upload confidential recordings.*"""
