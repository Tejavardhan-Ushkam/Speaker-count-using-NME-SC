# Lovable prompts: the client-facing SpeakerCount website

**How the pieces fit:**
- The **Hugging Face Space** (`Teja-vardhan006/speaker-count`) is the engine. It runs the model and has an API.
- The **Lovable site** is the product clients see: branded and polished. It sends audio to the engine and presents the result.
- Clients never see Hugging Face.

The free plan allows 3 prompts. Prompt 1 builds the complete site, Prompt 2 is only for fixes, and Prompt 3 is for branding at the end.

**Checked on the live Space** (2026-11-23):
- endpoint `/predict` takes one input named `audio` and returns the JSON result;
- endpoint `/model_info` takes no input;
- calls from other websites (CORS) are allowed.

---

## Prompt 1 — build the complete site (paste everything inside the box)

```
Build "SpeakerCount", a polished, vibrant, client-facing marketing website plus a working web app that tells users how many
people speak in an audio recording, who spoke when, and how long each person talked. It must feel like a modern AI SaaS
product (think Linear / Vercel / Descript quality), not a student demo. Front-end only: do NOT add Supabase, a database,
authentication, edge functions, payments or any backend of your own.

=== THE ENGINE (already live; call it for real, never mock it) ===
The analysis runs on a public Hugging Face Gradio Space. Use the official npm package "@gradio/client" from the browser.
src/config.ts:
  export const SPACE_ID = "Teja-vardhan006/speaker-count";
src/lib/engine.ts:
  import { Client, handle_file } from "@gradio/client";
  let clientPromise: Promise<Client> | null = null;
  export function getClient() { if (!clientPromise) clientPromise = Client.connect(SPACE_ID); return clientPromise; }
  export async function analyse(file: File) {
    try { const c = await getClient(); const r = await c.predict("/predict", { audio: handle_file(file) }); return r.data[0]; }
    catch (e) { clientPromise = null; throw e; }
  }
  export async function engineInfo() { const c = await getClient(); return (await c.predict("/model_info", {})).data[0]; }
Endpoint names and the parameter name "audio" are exact. Errors arrive as exceptions with a readable message (e.g. a daily
GPU quota message, "could not decode audio", "audio is 45.0 min; the limit is 30 min"). Show these in friendly words with
the original text in a small "details" line. Never show raw stack traces.

/predict result (every field except num_speakers may be missing; never crash):
{
  "num_speakers": 4,
  "audio": {"duration_sec": 169.15, "speech_sec": 147.34},
  "speakers": [ {"id": 1, "label": "Speaker 1", "talk_time_sec": 61.5, "share": 0.441},
                {"id": 2, "label": "Speaker 2", "talk_time_sec": 36.0, "share": 0.258} ],
  "turns": [ {"speaker": 1, "start": 2.8, "end": 6.55}, {"speaker": 2, "start": 6.55, "end": 11.8} ],
  "notes": ["Less than 30 s of speech was detected; counts on very short audio are less reliable."],
  "diagnostics": {"n_segments": 154, "p_star": 11, "gap_ratio": 5.721, "eigenvalues": [0.0012, 0.0705, 0.0867, 0.1586, 3.4808, 3.5983],
                  "time_vad_sec": 1.2, "time_embed_sec": 0.4, "time_cluster_sec": 0.2},
  "processing_sec": 2.1,
  "model": {"name": "NME-SC on ECAPA speaker embeddings (p_min 4)", "version": "abc1234",
            "measured_accuracy": {"VoxConverse test, 1-6 speakers (117 recordings)": {"exact": 0.64, "within_1": 0.86, "mae": 0.67},
                                  "VoxConverse test, all (232 recordings, 1-21 speakers)": {"exact": 0.46, "within_1": 0.64, "mae": 1.47},
                                  "AMI meetings test (16 meetings, 3-4 speakers)": {"exact": 0.69, "within_1": 0.94, "mae": 0.38}},
            "scope": "Most reliable for 1-6 speakers. With many speakers (10+) it tends to under-count."}
}
num_speakers can be 0 (no speech found): show a friendly empty state using notes.

Engine wake-up: the engine sleeps when unused. When the visitor first scrolls to or opens the app, call getClient() in the
background and show a small status chip: "Warming up the AI engine…" (spinner), then "Engine ready" (green dot), or
"Engine unavailable, Retry" (red). Uploading and recording stay usable while it warms up; "Analyse" waits for it.

=== SITE STRUCTURE (one page with smooth-scrolling sections + a sticky glass navbar) ===
Navbar: logo (a small sound-wave glyph and the wordmark "SpeakerCount"), links How it works · Use cases · Accuracy · FAQ,
and a gradient "Try it free" button that scrolls to the app.
1. HERO: big bold headline "Know who's talking. Instantly." with the subline "Upload any recording and our AI counts the speakers,
   maps who spoke when, and measures everyone's talk time, in seconds." Two CTAs: "Analyse a recording" (scrolls to the app)
   and "See how it works". Background: an animated mesh gradient (indigo → violet → fuchsia → amber, slowly moving) with
   an animated audio waveform made of bars, in several colours, that "separates" into coloured speaker lanes. Small trust row:
   "Works with MP3 · WAV · M4A · FLAC · OGG · WebM", "Up to 30 minutes", "Recordings not kept".
2. THE APP ("Try it now", id="app"): a large glass card.
   - Tabs: "Upload" (big drag-and-drop zone with an animated dashed border and an icon; file picker; accept audio/*; reject >100 MB
     with a clear message) and "Record" (MediaRecorder, a big pulsing record button, live timer, a live input-level meter, max 10 min,
     sends the result as File "recording.webm").
   - After choosing a file: name, size and duration chips, plus a custom audio player with a waveform (wavesurfer.js is fine).
   - Primary gradient button "Analyse". While running: an animated multi-step progress with icons ("Uploading" → "Detecting speech" →
     "Creating voice fingerprints" → "Grouping voices"), advancing on a timer (cosmetic), with elapsed seconds and a shimmer.
   - RESULTS (animated reveal):
     a) Hero result: a large animated count-up number "4", the text "speakers detected", and a row of coloured speaker avatars (circles
        labelled S1, S2…). Use a consistent palette of 12 vivid colours, cycling after that.
     b) Stat tiles: audio length, speech detected, processing time (formatted mm:ss / s).
     c) "Who spoke when": an interactive timeline, one lane per speaker, rounded coloured bars, a time axis (mm:ss), a hover tooltip
        (speaker, start–end, duration), click a bar to play that moment in the player, and a moving playhead synced to the player.
     d) "Talk time": a donut chart of shares plus a ranked list (avatar, mm:ss, %) with animated bars (recharts).
     e) Notes as soft amber callouts.
     f) Collapsible "For the technically curious": a line chart of the eigenvalues with the caption "The count is where the biggest jump
        is (the eigengap)", plus segments analysed, p*, gap ratio, timings and model name/version.
     g) Actions: "Download report (JSON)", "Download timeline (CSV: speaker,start,end)", "Analyse another recording".
3. HOW IT WORKS: 4 illustrated steps in cards with icons and connecting lines: "Find the speech" (voice activity detection),
   "Fingerprint every voice" (deep speaker embeddings, one every 0.75 s), "Connect similar voices" (similarity graph),
   "Count the groups" (spectral clustering: the eigengap reveals how many voices there are). One short plain-English sentence each.
4. USE CASES: 6 vibrant cards with icons: Meetings & stand-ups, Podcasts & interviews, Call-centre QA, Classrooms & lectures,
   Focus groups & research, Media monitoring. One line each about why the speaker count and talk time matter.
5. ACCURACY & LIMITS (honest, builds trust): load engineInfo() and render measured_accuracy as animated stat cards
   (exact %, within ±1 %, mean error) for each test set, with the scope sentence highlighted. Add the copy: "Measured on public
   benchmark recordings the model never saw during development. Best for 1–6 speakers; with very large groups it tends to
   under-count." If engineInfo() fails, show these fallback numbers: 64 % / 86 % (1–6 speakers), 46 % / 64 % (all), 69 % / 94 % (meetings).
6. PRIVACY: three short points with icons: "Processed only to produce your result", "Uploads are deleted automatically within an hour",
   "No account needed". Do not claim anything else (no encryption, compliance or certification claims).
7. FAQ (accordion): What files can I use? How long can a recording be (30 min, 100 MB)? How accurate is it? Why is the count
   sometimes off by one (overlapping speech, very short speakers, similar voices)? Is my audio stored? Does it identify who the
   speakers are (no: it distinguishes voices, it does not recognise identities)?
8. FINAL CTA band with a gradient: "Ready to see who's talking?" and the button "Analyse a recording".
Footer: logo, short description, section links, "Contact" (mailto:you@example.com placeholder) and © year.

=== LOOK & FEEL ===
Vibrant but professional: a dark-first design (deep navy background #0B1020) with a light-mode toggle; gradient accents
(indigo #6366F1 → violet #8B5CF6 → fuchsia #D946EF → amber #F59E0B); glassmorphism cards (backdrop blur, 1px translucent borders,
soft glow on hover); large rounded corners (2xl); generous spacing; the font "Plus Jakarta Sans" for headings and "Inter" for body text.
Tasteful motion with framer-motion: fade/slide-in on scroll, count-up numbers, hover lift; respect prefers-reduced-motion.
Fully responsive (phone, tablet, laptop projector), accessible (AA contrast, keyboard focus rings, aria labels, alt text).
Use shadcn/ui, Tailwind and lucide-react icons. Add favicon and meta/OG tags (title "SpeakerCount: who's talking, instantly").

Before finishing, verify: the app calls Client.connect("Teja-vardhan006/speaker-count") and then predict("/predict", { audio: handle_file(file) })
and reads result.data[0]; no Content-Type header is set manually; nothing is mocked; and every result field is optional except num_speakers.
```

---

## Prompt 2 — fixes only (fill in, then send everything at once)

Copy the exact error from the browser (right-click → Inspect → Console), and list every problem in one message.

```
Fix all of these in one pass; do not redesign or change anything else:
1. <what you saw, e.g. "Engine ready" never appears. Console: ...>
2. <e.g. Analyse fails with: ...>
3. <e.g. the timeline overflows on phones / the donut colours do not match the lanes>
Keep the engine call exactly: Client.connect("Teja-vardhan006/speaker-count") then
client.predict("/predict", { audio: handle_file(file) }), and read result.data[0].
```

## Prompt 3 — branding (keep for last)

```
Content and branding update only (no logic or layout changes): set the product name to "<name>", use this tagline "<tagline>",
set the contact e-mail to <email>, add "<company or your name>" in the footer, and use <colour hex> as the primary accent.
```

---

## After Lovable has built it

1. **Test in the preview:**
   - the engine chip turns green;
   - an upload gives a result;
   - recording works;
   - the downloads work;
   - the page looks right on a phone-sized window.
2. **Publish** (top right) to get `https://<project>.lovable.app`. That's the link for clients.
3. **Optional: your own domain.** Lovable's **Settings → Domains** connects one, such as `speakercount.yourname.com`. This needs a paid Lovable plan.
4. **Optional: connect GitHub** under **Settings → GitHub**. Lovable then keeps the site's code in a repository you own, and you can make small text edits there without using prompts.

**GPU allowance:**
- **Who pays:** each analysis uses a few seconds of the free daily ZeroGPU allowance. Visitors who aren't logged in to Hugging Face draw on an allowance shared by IP address.
- **Light client traffic:** that's enough.
- **Steady paying clients:** upgrade the Space's hardware, or move the engine to the Docker version in `deploy/hf_space_docker/` on paid CPU. The website doesn't change, because it only talks to the engine.
