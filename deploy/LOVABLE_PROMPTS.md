# Lovable prompts (optional)

The Hugging Face Space at https://teja-vardhan006-speaker-count.hf.space is already a complete website.
Use Lovable only if you want a second, custom-designed front-end.

The free plan allows 3 prompts, so each one does a lot. Before using them, make sure the Space shows **Running** and that analysing a file on its own page works.

---

## Prompt 1 — build the whole site (paste the full block)

```
Build a polished, single-page web app called "SpeakerCount" that counts how many people speak in an audio recording.
It is a demo of a university research project, to be shown to a professor. It is a front-end only:
do NOT add Supabase, a database, authentication, edge functions or any backend.

The analysis runs on an existing public Hugging Face Gradio Space. Call it from the browser with the official
Gradio JavaScript client: install the npm package "@gradio/client". Do not mock it; call it for real.
Put the Space id in one file, src/config.ts:
export const SPACE_ID = "Teja-vardhan006/speaker-count";
export const SPACE_URL = "https://teja-vardhan006-speaker-count.hf.space";

How to call it (src/lib/api.ts):
import { Client, handle_file } from "@gradio/client";
let clientPromise = null;
export function getClient() { if (!clientPromise) clientPromise = Client.connect(SPACE_ID); return clientPromise; }
export async function countSpeakers(file: File) {
  const client = await getClient();
  const res = await client.predict("/predict", { audio: handle_file(file) });
  return res.data[0];            // the JSON result described below
}
export async function modelInfo() {
  const client = await getClient();
  return (await client.predict("/model_info", {})).data[0];
}
If the connection or the call fails, reset clientPromise to null so the next attempt reconnects.
Errors raised by the Space arrive as exceptions whose message is human-readable (for example a GPU-quota or
"could not decode audio" message); show that text to the user.

The /predict result looks like this (treat every field except num_speakers as optional):
{
  "num_speakers": 4,
  "audio": {"duration_sec": 169.15, "speech_sec": 147.34},
  "speakers": [
    {"id": 1, "label": "Speaker 1", "talk_time_sec": 61.5, "share": 0.441},
    {"id": 2, "label": "Speaker 2", "talk_time_sec": 36.0, "share": 0.258}
  ],
  "turns": [ {"speaker": 1, "start": 2.8, "end": 6.55}, {"speaker": 2, "start": 6.55, "end": 11.8} ],
  "notes": [],
  "diagnostics": {"n_segments": 154, "k_before_postprocessing": 4, "p_star": 11, "gap_ratio": 5.721,
                  "eigenvalues": [0.00116, 0.0705, 0.08669, 0.1586, 3.48076, 3.59828],
                  "time_vad_sec": 1.2, "time_embed_sec": 0.4, "time_cluster_sec": 0.2},
  "processing_sec": 2.1,
  "device": "cuda",
  "model": {"name": "NME-SC on ECAPA speaker embeddings (p_min 4)", "method": "nmesc_ecapa", "version": "abc1234",
            "k_max": 25, "p_min": 4,
            "measured_accuracy": {"VoxConverse test, 1-6 speakers (117 recordings)": {"exact": 0.64, "within_1": 0.86, "mae": 0.67}},
            "scope": "Most reliable for 1-6 speakers. With many speakers (10+) it tends to under-count."}
}
num_speakers can be 0 (no speech found); then speakers and turns are empty and notes explains why.

The Space sleeps when unused. On page load, call getClient() and show a banner "Waking up the analysis server
(can take 1-3 minutes)" with a spinner until it connects. Then show a green "Server ready" pill, load modelInfo()
for the About section, and show a red message with a Retry button on failure. Keep the upload controls usable the whole time.

Page layout (responsive, looks good on a laptop projector and on a phone):
- Header: app name "SpeakerCount", subtitle "How many people are speaking? Upload a recording and find out.", and the server status pill.
- Input card with two tabs:
  (a) "Upload file": a drag-and-drop zone plus a file picker; accept audio/* (wav, mp3, m4a, flac, ogg, webm). Reject files
      over 100 MB with a clear message. Show the file name, size and duration, and an audio player to preview it.
  (b) "Record": record from the microphone with MediaRecorder (Start/Stop, live timer, max 10 minutes), then preview it and send it as a File named "recording.webm".
  A primary button "Count speakers".
- While analysing: a progress state with step text that changes every few seconds ("Uploading", "Detecting speech",
  "Extracting voice fingerprints", "Clustering speakers"), plus elapsed seconds.
- Results:
  1. A hero line, "4 speakers detected" (singular for 1; for 0 say "No speech detected").
  2. Stat cards: audio length, speech detected, processing time.
  3. "Who spoke when": a horizontal timeline over the audio length, one row per speaker, coloured bars for the turns.
     Hovering a bar shows the speaker and its start-end time (mm:ss); clicking a bar seeks the preview player there and plays it.
  4. "Talk time": a horizontal bar chart (recharts) of talk_time_sec per speaker, with percentages.
  5. Notes as amber info boxes.
  6. A collapsible "Technical details" panel: model name and version, k_max, p_min, n_segments, p_star, gap_ratio, timings, device,
     and a small line chart of the eigenvalues captioned "The count is the position of the largest jump (eigengap)".
  7. Buttons "Download JSON" and "Analyse another file".
- "About the model" section: five steps (speech detection → 1.5 s windows → ECAPA speaker embeddings → graph of nearest
  neighbours → NME-SC spectral clustering, count = largest eigengap). Show measured_accuracy as a table (test set, exact,
  within ±1, MAE) and the scope text prominently. Add a link "Open the original demo on Hugging Face" to SPACE_URL.
- Footer: "Research prototype. Audio is processed only for this request and is not stored." Add a link to
  https://github.com/Tejavardhan-Ushkam/Speaker-count-using-NME-SC

Style: clean, modern, light theme with a dark-mode toggle, indigo accent, rounded cards, shadcn/ui + Tailwind, accessible contrast,
and a consistent palette of 12 speaker colours. Show errors as toasts and inline.
```

---

## Prompt 2 — only if something is wrong (fill in what you saw)

Use it to fix every problem at once. Replace the bullets with what you observed, and paste the exact error text
from the browser console (right-click → Inspect → Console).

```
Fix these issues in one pass, and do not change anything else:
1. <e.g. "Server ready" never appears. Console: ...>
2. <e.g. Clicking "Count speakers" fails with: ...>
3. <e.g. The timeline overflows on mobile>
Re-check that the app uses @gradio/client: Client.connect("Teja-vardhan006/speaker-count"), then
client.predict("/predict", { audio: handle_file(file) }), and reads res.data[0].
```

## Prompt 3 — keep in reserve

For one last content change before the presentation:

```
Small content update only: in the header add "M.Tech project by <your name>, supervised by <prof name>, <university>".
Do not change any logic.
```
