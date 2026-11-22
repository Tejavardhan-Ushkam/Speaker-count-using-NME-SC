---
title: Speaker Count API
emoji: 🎙️
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Speaker Count API

Counts the speakers in an uploaded audio file.

**Pipeline:** pyannote speech detection → ECAPA speaker embeddings → NME-SC graph → SpectralNet → cluster post-processing.

**Endpoints:**
- `GET /` — test page for uploading a file
- `GET /health` — whether the server is ready
- `GET /model` — description of the model
- `POST /predict` — send the audio as multipart field `file`

**Required Space secret:** `HF_TOKEN`, a Hugging Face read token. Its account must have accepted the conditions of `pyannote/segmentation-3.0`.

Uploaded audio is processed in a temporary folder and deleted after the request.
