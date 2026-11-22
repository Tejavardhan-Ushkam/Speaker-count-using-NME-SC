# Deploying SpeakerCount on Hugging Face: step by step

**Result:** a public website at **https://teja-vardhan006-speaker-count.hf.space**.

- It opens from any network, and the college server can be switched off.
- Your professor uploads or records audio and sees the number of speakers, a "who spoke when" timeline and talk time per speaker.
- The model behind it is **NME-SC on ECAPA speaker embeddings (p_min 4)**.

**Your accounts:**
- GitHub: `Tejavardhan-Ushkam`
  - repository `https://github.com/Tejavardhan-Ushkam/Speaker-count-using-NME-SC`
- Hugging Face: `Teja-vardhan006`
  - Space page `https://huggingface.co/spaces/Teja-vardhan006/speaker-count`
  - website `https://teja-vardhan006-speaker-count.hf.space` (always lower case)

All commands below are run in your SSH session on the college server, because the files are there.
Total time is about 45 minutes, most of it waiting for the build.

---

## What Docker is, and what you need to do with it

You don't need to install or run Docker. Hugging Face runs it for you.

- **The problem it solves:** the model needs a specific setup to run: Python 3.10, PyTorch 2.6, SpeechBrain, pyannote, ffmpeg and so on.
- **What it does:** Docker writes that whole setup down as a recipe, so any computer can rebuild it exactly.
- **The recipe:** `deploy/hf_space/Dockerfile`. It has 8 short steps:
  1. start from a clean Linux with Python 3.10;
  2. install ffmpeg (audio decoding) and libsndfile;
  3. create the user account Hugging Face requires (id 1000);
  4. install CPU-only PyTorch, then the pinned packages in `requirements.txt`;
  5. copy our code (`speakercount/`, `configs/`, `deploy/model.yaml`, `app.py`, `static/index.html`);
  6. download the ECAPA speaker model into the image, so it's ready at start-up;
  7. open port 7860;
  8. start the web server: `uvicorn app:app`.
- **Your part:** upload the folder that contains this recipe (Step 4). Hugging Face builds the **image**, which is the finished setup,
  then starts it as a **container**, a running copy. The Space's **Logs** tab shows each recipe step as it runs.
  "Building" means the image is being made, and "Running" means the website is live.

---

## Step 1 — Upload the project to your GitHub repository (10 min)

I've already linked the project to your repository (`git remote -v` shows `origin`). Nothing has been uploaded yet.

1. **Create a GitHub token,** which git uses instead of your password:
   1. Open https://github.com/settings/personal-access-tokens/new.
   2. Name: `server-push`. Expiration: 90 days.
   3. Under *Repository access*, choose **Only select repositories** and pick `Speaker-count-using-NME-SC`.
   4. Under *Permissions → Repository permissions → Contents*, choose **Read and write**.
   5. Click **Generate token** and copy it (it starts with `github_pat_`). It's shown only once, so keep it in a safe note.
2. **Set your name for this project only.** This doesn't change anyone else's settings on the server.
   ```bash
   cd "/DATA/mtp2026/SpecClustering v2"
   git config user.name  "Tejavardhan Ushkam"
   git config user.email "<the e-mail of your GitHub account>"
   ```
3. **Upload:**
   ```bash
   git push -u origin master --tags
   ```
   - *Username:* `Tejavardhan-Ushkam`
   - *Password:* paste the token. The terminal shows nothing while you paste; that's normal. Then press Enter.
4. **Check:** open the repository page and refresh. You should see the code, `reports/`, `results/`, `deploy/` and the tags.

**What's uploaded and what isn't:**
- About 17 MB of code, reports and results.
- Datasets, model checkpoints and caches stay on the server (they are listed in `.gitignore`).
- The commits made so far are recorded under the name configured on this server earlier, not yours. Commits from now on use your name.

**Later uploads:**
```bash
cd "/DATA/mtp2026/SpecClustering v2" && git push && git push --tags
```

---

## Step 2 — Hugging Face tokens and the speech-detection model (5 min)

1. **Read token,** used by the website to download the speech detector:
   1. Open https://huggingface.co/settings/tokens and click **Create new token**.
   2. Choose type **Read** and name it `space-runtime`.
   3. Create it and copy it (it starts with `hf_`).
2. **Write token,** used to upload code: create a second token of type **Write**, named `push`, and copy it.
3. **Accept the conditions of the speech-detection model:**
   1. While logged in as `Teja-vardhan006`, open https://huggingface.co/pyannote/segmentation-3.0.
   2. Fill in the short form (company/university, website) and click to accept.
   3. The page should then say you have access. Without this the website can't start.

Never put a token in a file, in code or in a commit. They go only into the places named below.

---

## Step 3 — Create the Space (3 min)

1. Open https://huggingface.co/new-space.
2. Fill in the form:
   - **Owner:** `Teja-vardhan006`
   - **Space name:** `speaker-count`. Use exactly this name: it's part of the website address.
   - **Licence:** `mit`, or whatever your mentor prefers.
   - **SDK:** **Docker**, template **Blank**.
   - **Hardware:** **CPU basic · 2 vCPU · 16 GB · FREE**.
   - **Visibility:** **Public**. Your professor can't open a private Space without an account.
3. Click **Create Space**. It shows a placeholder page for now.
4. **Add the token as a secret:**
   1. Open the Space's **Settings** tab and scroll to **Variables and secrets**.
   2. Click **New secret**.
   3. *Name:* `HF_TOKEN`, exactly like that. *Value:* paste the **Read** token.
   4. Click **Save**.

---

## Step 4 — Upload the website code to the Space (5 min)

```bash
cd "/DATA/mtp2026/SpecClustering v2"
./deploy/build_space.sh                      # gathers code + settings into deploy/space_build/ (about 300 KB)
cd deploy/space_build
git init -b main                             # only the first time
git config user.name  "Tejavardhan Ushkam"
git config user.email "<the e-mail of your Hugging Face account>"
git add -A && git commit -m "Speaker count website"
git remote add space https://huggingface.co/spaces/Teja-vardhan006/speaker-count   # only the first time
git push --force space main
```

- *Username:* `Teja-vardhan006`
- *Password:* the **Write** token (`push`).
- `--force` is needed only this first time, to replace the placeholder README in the new Space.

---

## Step 5 — Watch the build (15 min, just waiting)

1. Open https://huggingface.co/spaces/Teja-vardhan006/speaker-count. The badge next to the name shows the stage:
   - **Building:** Hugging Face is following the Dockerfile recipe. Click **Logs → Build** to watch it.
     The longest part is installing PyTorch and the other packages (5–10 min).
   - **Running:** the website is live. In **Logs → Container** you'll see `Uvicorn running on http://0.0.0.0:7860`.
   - **Build error** or **Runtime error:** see the troubleshooting table at the end.
2. Right after **Running**, the model loads for about 1–2 minutes. During that time the page shows "Loading the model…".

---

## Step 6 — Test it (5 min)

1. Open **https://teja-vardhan006-speaker-count.hf.space/health**. It should show `"status":"ready"`.
2. Open **https://teja-vardhan006-speaker-count.hf.space**. The status pill should be green ("Server ready").
3. Upload a short clip (mp3, wav, m4a and so on) and click **Count speakers**. You should get the number, the timeline and the talk-time bars.
   On the free CPU, expect about 10–30 s for a 3-minute file.
4. Try the **Record** tab with your laptop's microphone. The browser asks for permission once.
5. Open the link on your phone using mobile data to confirm it works away from the college network.

That address is the link to send your professor.

---

## Step 7 (optional) — A Lovable front-end

The Space already serves a complete website, so Lovable isn't needed.

If you also want a Lovable version, paste Prompt 1 from `deploy/LOVABLE_PROMPTS.md`. Its `API_BASE` already points to your Space, and it uses the same API.

---

## Before the presentation

- **Wake the Space early.** A free Space goes to sleep after about 48 hours without visitors.
  Open the website **10 minutes before** the meeting; it wakes up by itself in 1–3 minutes.
- **Have three clips ready:** 1 speaker, 2 speakers, and a 4-speaker meeting excerpt (2–5 minutes each).
- **Limits:** 100 MB per file and 30 minutes of audio, set in `app.py`. One file is analysed at a time.
- **Accuracy to quote** (held-out test sets, with the same automatic speech detection the website uses):

  | Test set | Exact count | Within ±1 | Mean error |
  |---|---|---|---|
  | VoxConverse, 1–6 speakers (117 recordings) | 64 % | 86 % | 0.67 |
  | VoxConverse, all (232 recordings, 1–21 speakers) | 46 % | 64 % | 1.47 |
  | AMI meetings (16 meetings) | 69 % | 94 % | 0.38 |

  With many speakers (10 or more) it tends to under-count.
- **Privacy:** audio goes to a temporary folder, is analysed and deleted. Nothing is stored. The Space is public, so don't demo with confidential recordings.

## Updating the website later

For example, to serve a different model: edit `deploy/model.yaml`, then:

```bash
cd "/DATA/mtp2026/SpecClustering v2" && ./deploy/build_space.sh
cd deploy/space_build && git add -A && git commit -m "update" && git push space main
```

The Space rebuilds by itself in about 10 minutes.

## Troubleshooting

| What you see | Cause | Fix |
|---|---|---|
| Logs: `GatedRepoError`, `401` or `403` for `pyannote/segmentation-3.0`; `/health` shows `"status":"error"` | Model conditions not accepted, or secret missing or misnamed | Redo Step 2.3, check that the secret is called exactly `HF_TOKEN`, then **Settings → Restart this Space** |
| Build error at a `pip install` line | A download failed during the build | **Settings → Factory rebuild**. If the same line fails again, copy about 20 log lines and ask for help |
| `git push` says `Authentication failed` | A normal password was used, or the wrong token | GitHub: the `github_pat_…` token. Hugging Face: the **Write** token |
| `git push` to the Space is rejected (`non-fast-forward`) | The Space already has a commit | The first time, use `git push --force space main` |
| The page says "Waking up the server" for more than 4 minutes | The Space is restarting or broken | Look at the Space page badge and its **Logs** |
| `413` | File larger than 100 MB | Shorter clip, or set `MAX_UPLOAD_MB` under Space **Settings → Variables** |
| `422 could not decode audio` | Unusual file format | Convert to mp3 or wav first |
| Count looks wrong on a very short clip (under 30 s) | Too little speech to tell voices apart | Use at least 1 minute of speech; the site shows a warning for short clips |

## Files

| Path | Purpose |
|---|---|
| `deploy/model.yaml` | Which model the website serves, its settings and measured accuracy |
| `deploy/hf_space/app.py` | Web server (FastAPI): `/` website, `/health`, `/model`, `/predict` |
| `deploy/hf_space/static/index.html` | The website: upload or record, result, timeline, talk time, technical details |
| `deploy/hf_space/Dockerfile`, `requirements.txt` | The Docker recipe and pinned packages |
| `deploy/build_space.sh` | Gathers the files above plus `speakercount/` into `deploy/space_build/` |
| `speakercount/infer.py` | Counts speakers in one audio file. Test it locally with `python run.py predict --audio file.mp3` |
