"""Speaker Count: Gradio app for a Hugging Face ZeroGPU Space.

Website: upload or record audio, then see the count, "who spoke when", talk time and the raw JSON.
API (from gradio_client / @gradio/client):
  /predict    (audio file) -> JSON result (num_speakers, speakers, turns, notes, diagnostics, model ...)
  /model_info ()           -> model description and measured accuracy
"""

from __future__ import annotations

import gradio as gr
import spaces

from app_core import COUNTER, about_md, analyse, summary_md, timeline_fig


@spaces.GPU(duration=90)
def predict(audio: str) -> dict:
    """Count the speakers in an audio file. Returns the full JSON result."""
    if not audio:
        raise gr.Error("Please upload or record an audio file first.")
    try:
        return analyse(audio)
    except ValueError as e:  # undecodable or too long
        raise gr.Error(str(e)) from e


def model_info() -> dict:
    """Model description, settings and measured accuracy."""
    return COUNTER.info()


def run_ui(audio: str):
    r = predict(audio)
    return summary_md(r), timeline_fig(r) if r.get("speakers") else None, r


with gr.Blocks(title="Speaker Count") as demo:
    gr.Markdown("# 🎙️ SpeakerCount\nHow many people are speaking? Upload or record audio and find out.")
    with gr.Row():
        with gr.Column(scale=1):
            audio = gr.Audio(sources=["upload", "microphone"], type="filepath", label="Audio (wav, mp3, m4a, flac, ogg, webm)")
            btn = gr.Button("Count speakers", variant="primary")
            gr.Markdown("Up to 30 minutes per file. The first analysis after a quiet period takes longer while the server wakes up.")
        with gr.Column(scale=2):
            out_md = gr.Markdown("Results appear here.")
            out_plot = gr.Plot(label="Who spoke when")
    with gr.Accordion("Technical details (JSON)", open=False):
        out_json = gr.JSON()
    with gr.Accordion("About the model", open=False):
        gr.Markdown(about_md())
    btn.click(run_ui, inputs=audio, outputs=[out_md, out_plot, out_json], api_name="count_ui")
    # clean API endpoints (shown under "Use via API" at the bottom of the page)
    gr.Button(visible=False).click(predict, inputs=audio, outputs=out_json, api_name="predict")
    gr.Button(visible=False).click(model_info, inputs=None, outputs=out_json, api_name="model_info")

demo.queue(max_size=20).launch(max_file_size="100mb")
