---
title: Speaker Count
emoji: 🎙️
colorFrom: indigo
colorTo: blue
sdk: gradio
python_version: "3.10"
app_file: app.py
pinned: false
short_description: Counts how many people speak in an audio recording
---

# Speaker Count

Counts how many people speak in an uploaded or recorded audio file, and shows who spoke when.

**Pipeline:** pyannote speech detection → 1.5 s windows → ECAPA speaker embeddings → NME-SC spectral clustering. The count is the largest eigengap.

**API** (the page's footer has "Use via API"):
- `/predict` takes an audio file and returns JSON.
- `/model_info` returns the model description and its measured accuracy.

**Required Space secret:** `HF_TOKEN`, a read token. Its account must have accepted the conditions of `pyannote/segmentation-3.0`.

Uploaded audio is processed for the request only and is not stored.
