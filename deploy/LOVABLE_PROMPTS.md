# Lovable prompts (free plan: 3 prompts, so each one does a lot)

Do this only after the back-end is live (step 3 of DEPLOY_GUIDE.md) and
`https://<your-hf-username>-speaker-count.hf.space/health` shows `"status":"ready"`.

Before pasting, replace `YOUR-HF-USERNAME` with your Hugging Face username in lower case.
The URL appears exactly once in Prompt 1, on the `API_BASE` line.

---

## Prompt 1 — build the whole site (paste the full block)

```
Build a polished, single-page web app called "SpeakerCount" that counts how many people speak in an audio recording.
It is a demo of a university research project, to be shown to a professor. It is a front-end only:
do NOT add Supabase, a database, authentication, edge functions or any backend. The browser calls an existing public REST API directly (CORS is open).

API (already deployed; do not mock it, call it for real):
const API_BASE = "https://YOUR-HF-USERNAME-speaker-count.hf.space";
Put API_BASE in one file, src/config.ts, and import it everywhere.

Endpoints:
1. GET  {API_BASE}/health  -> {"status":"ready"|"loading"|"error","error":string|null,"busy":boolean,"max_upload_mb":100,"max_audio_min":30}
2. GET  {API_BASE}/model   -> model description (see example below, the "model" object)
3. POST {API_BASE}/predict -> multipart/form-data with ONE field named "file" (the audio file). Returns JSON like:
{
  "filename": "meeting.mp3",
  "num_speakers": 4,
  "audio": {"duration_sec": 169.15, "speech_sec": 147.34},
  "speakers": [
    {"id": 1, "label": "Speaker 1", "talk_time_sec": 61.5, "share": 0.441},
    {"id": 2, "label": "Speaker 2", "talk_time_sec": 36.0, "share": 0.258},
    {"id": 3, "label": "Speaker 3", "talk_time_sec": 18.75, "share": 0.134},
    {"id": 4, "label": "Speaker 4", "talk_time_sec": 23.2, "share": 0.167}
  ],
  "turns": [ {"speaker": 1, "start": 2.8, "end": 6.55}, {"speaker": 2, "start": 6.55, "end": 11.8} ],
  "notes": [],
  "diagnostics": {"n_segments": 154, "k_before_postprocessing": 4, "p_star": 11, "gap_ratio": 5.721,
                  "eigenvalues": [0.00116, 0.0705, 0.08669, 0.1586, 3.48076, 3.59828],
                  "time_vad_sec": 5.9, "time_embed_sec": 3.3, "time_cluster_sec": 0.7},
  "processing_sec": 10.1,
  "model": {"name": "SpecClustering v2 (ECAPA + NME-SC graph + SpectralNet + pruning)", "method": "snet_ecapa_pp",
            "version": "abc1234", "k_max": 25, "p_min": 4,
            "postprocess": {"min_cluster_share": 0.15, "share_mode": "relative", "merge_threshold": 0.7, "single_speaker_threshold": null},
            "measured_accuracy": {"VoxConverse test, 1-6 speakers (117)": {"exact": 0.59, "within_1": 0.84, "mae": 0.65}},
            "scope": "Best on recordings with 1-6 speakers; above 10 speakers it under-counts."}
}
Errors come back as HTTP 4xx/5xx with JSON {"detail": "message"}: 413 file too large, 422 cannot decode or too long, 429 busy, 503 model still loading.
num_speakers can be 0 (no speech found); then speakers and turns are empty and notes explains why.
Treat every field except num_speakers as optional and never crash on a missing field.

The server is on a free host that sleeps when unused. On page load, call /health. If the request fails or the status is "loading",
show a friendly banner "Waking up the analysis server, this can take up to 3 minutes" with a spinner, and poll /health every 5 s
for up to 4 minutes. Show a green "Server ready" pill once the status is "ready", or a red message with a Retry button if it is still not ready after 4 minutes.
Keep the upload controls usable the whole time, but queue the analysis until the server is ready.

Page layout (responsive, looks good on a laptop projector and on a phone):
- Header: app name "SpeakerCount", subtitle "How many people are speaking? Upload a recording and find out.", server status pill.
- Input card with two tabs:
  (a) "Upload file": drag-and-drop zone plus a file picker. Accept audio/* and video/* (wav, mp3, m4a, flac, ogg, webm, mp4).
      Reject files over 100 MB in the browser with a clear message. Show the file name, size and duration (from an <audio> element), and an audio player to preview it.
  (b) "Record": record from the microphone with MediaRecorder (Start / Stop, live timer, max 10 minutes), then preview and send it
      as a File named "recording.webm".
  A primary button "Count speakers".
- While analysing: a progress state with step text that changes every few seconds ("Uploading", "Detecting speech", "Extracting voice
  fingerprints", "Clustering speakers"). This is cosmetic only, because the API returns once at the end. Show the elapsed seconds. Use a fetch timeout of 10 minutes.
- Results section (appears below; keep the last result visible until a new one arrives):
  1. A large hero number: "4 speakers detected" (singular for 1; for 0 show "No speech detected").
  2. Small stat cards: audio length, speech detected, processing time.
  3. "Who spoke when": a horizontal timeline over the audio length, with one row per speaker and coloured bars for each turn.
     Hovering a bar shows the speaker and start-end time (mm:ss). Clicking a bar seeks the audio preview player to that time and plays it.
  4. "Talk time": a horizontal bar chart (recharts) of talk_time_sec per speaker with percentages.
  5. Any notes shown as amber info boxes.
  6. A collapsible "Technical details" panel: model name, version, k_max, p_min, post-processing settings, n_segments,
     k_before_postprocessing, p_star, gap_ratio, timings, and a small line chart of the first eigenvalues (x = index 1..n,
     y = eigenvalue), with the caption "The count is the position of the largest jump (eigengap)".
  7. Buttons: "Download JSON" (the raw response) and "Analyse another file".
- "About the model" section (load it from GET /model once the server is ready): explain the pipeline in five steps
  (speech detection → 1.5 s windows → ECAPA speaker embeddings → similarity graph and spectral clustering with SpectralNet → removal of
  tiny clusters). Show measured_accuracy as a small table (dataset, exact, within ±1, MAE) and show "scope" prominently, with the text:
  "Accuracy was measured on held-out test sets. It is highest for 1-6 speakers, and the model tends to under-count very large groups."
- Footer: "Research prototype. Audio is processed on the server only for this request and is not stored." Add a GitHub link placeholder (href="#").

Style: clean, modern, light theme with an optional dark mode toggle, indigo accent, rounded cards, plenty of whitespace,
accessible contrast, and a consistent speaker colour palette (up to 12 distinct colours, cycling after that). Use shadcn/ui and Tailwind.
Show errors as toasts and also inline in the result area, using the API "detail" text.
After building, double-check that the request uses FormData with the field name exactly "file", that you do NOT set the
Content-Type header manually, and that API_BASE has no trailing slash.
```

---

## Prompt 2 — only if something is wrong (fill in what you saw)

Use it to fix all problems at once. Replace the bullets with what you observed, and paste the exact error text
from the browser (right-click → Inspect → Console).

```
Fix these issues in one pass, and do not change anything else:
1. <e.g. Clicking "Count speakers" shows "Failed to fetch". Console: ...>
2. <e.g. The timeline overflows on mobile>
3. <e.g. The status pill stays on "Waking up" although {API_BASE}/health returns {"status":"ready"}>
Re-check that POST {API_BASE}/predict sends FormData with the field "file", with no manual Content-Type header and no trailing slash in API_BASE.
```

## Prompt 3 — keep in reserve

Keep it for the day before the presentation, for one last change; for example adding your name, the professor's name,
the university logo and a link to the repository in the header and footer:

```
Small content update only: in the header add "M.Tech project by <your name>, supervised by <prof name>, <university>"; in the footer
replace the GitHub placeholder link with <repo URL>. Do not change any logic.
```

Free fixes that don't use a prompt:
- Lovable's code view, or the GitHub sync described in DEPLOY_GUIDE.md, lets you edit text such as `API_BASE` in `src/config.ts` by hand.
- After editing, press **Publish** again.
