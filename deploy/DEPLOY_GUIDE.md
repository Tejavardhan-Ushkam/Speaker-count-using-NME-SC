# Deploying SpeakerCount on Hugging Face (Gradio + ZeroGPU): step by step

**Result:** a public website at **https://teja-vardhan006-speaker-count.hf.space**. It opens from any network, and the college server can be off.

On the page you can:
- upload or record audio;
- see the number of speakers, a "who spoke when" chart and talk time per speaker;
- open the raw JSON and an "About the model" section.

**The model:** NME-SC on ECAPA speaker embeddings (p_min 4), with pyannote speech detection.

| | |
|---|---|
| GitHub repository | https://github.com/Tejavardhan-Ushkam/Speaker-count-using-NME-SC |
| Hugging Face Space | https://huggingface.co/spaces/Teja-vardhan006/speaker-count (Gradio SDK, ZeroGPU, public) |
| Website | https://teja-vardhan006-speaker-count.hf.space (always lower case) |

Run every command in your SSH session on the college server, where the files are.

## How the Space works (no Docker needed)

On the free plan only Gradio Spaces are available, so we don't use Docker. Hugging Face prepares the environment from three plain files:

| File | What Hugging Face does with it |
|---|---|
| `README.md` (top block) | `sdk: gradio`, so it installs Gradio and runs `app.py` |
| `packages.txt` | Linux packages: `ffmpeg` (decodes mp3, m4a, webm…) and `libsndfile1` |
| `requirements.txt` | Python packages: PyTorch, SpeechBrain, pyannote, `spaces` and so on |

**ZeroGPU** lends the Space a GPU **only while a file is being analysed**: that's the function marked `@spaces.GPU` in `app.py`.
The rest of the time the Space runs on CPU.

- Each analysis uses a few seconds of GPU time.
- Visitors get a free daily GPU allowance, which is larger if they're logged in to Hugging Face. That's more than enough for a demo.

---

## Step 1 — Upload the project to GitHub (10 min)

The project is already linked to your repository (`origin`); nothing has been uploaded yet.

1. **Create a token** at https://github.com/settings/personal-access-tokens/new:
   - name: `server-push`, expiration 90 days;
   - *Repository access*: **Only select repositories**, then pick `Speaker-count-using-NME-SC`;
   - *Repository permissions → Contents*: **Read and write**;
   - click **Generate** and copy the token (`github_pat_…`). It's shown only once.
2. **Set your name and upload:**
   ```bash
   cd "/DATA/mtp2026/SpecClustering v2"
   git config user.name  "Tejavardhan Ushkam"              # this project only
   git config user.email "<your GitHub account e-mail>"
   git push -u origin master --tags
   ```
   - *Username:* `Tejavardhan-Ushkam`
   - *Password:* paste the token. Nothing appears while you paste; that's normal.
3. **Check:** refresh the repository page. You should see the code, reports, results and `deploy/`.
   The datasets and model files are not uploaded; that's intended.

---

## Step 2 — Hugging Face: model access and the secret (5 min)

You've already created the Space. Now:

1. **Accept the speech-detector conditions:**
   1. While logged in as `Teja-vardhan006`, open https://huggingface.co/pyannote/segmentation-3.0.
   2. Fill in the short form and accept.
   3. The page should then say you have access. Without this the Space can't start.
2. **Add the secret:**
   1. In your Space, open **Settings → Variables and secrets → New secret**.
   2. *Name:* `HF_TOKEN`, exactly. *Value:* your **Read** token.
   3. Click **Save**.
3. **Note the Gradio version Hugging Face chose.** This keeps the code and the platform on the same version.
   1. In your Space, open the **Files** tab and click `README.md`.
   2. Find the line `sdk_version: …` (for example `sdk_version: 5.49.1`) and copy it.
   3. On the server, open `deploy/hf_space/README.md` and paste it **directly under** the line `sdk: gradio`. Save.
   4. If there is no such line, skip this step.

---

## Step 3 — Upload the website code to the Space (5 min)

```bash
cd "/DATA/mtp2026/SpecClustering v2"
./deploy/build_space.sh                     # gathers code + settings into deploy/space_build/ (~300 KB)
cd deploy/space_build
git init -b main                            # first time only
git config user.name  "Tejavardhan Ushkam"
git config user.email "<your Hugging Face account e-mail>"
git add -A && git commit -m "Speaker count website"
git remote add space https://huggingface.co/spaces/Teja-vardhan006/speaker-count   # first time only
git push --force space main
```

- *Username:* `Teja-vardhan006`
- *Password:* your **Write** token. Never paste a token into a file or a chat.
- `--force` (first time only) replaces the starter files Hugging Face put in the new Space.

**Later updates:**
```bash
cd "/DATA/mtp2026/SpecClustering v2" && ./deploy/build_space.sh
cd deploy/space_build && git add -A && git commit -m "update" && git push space main
```

---

## Step 4 — Watch it start (10–15 min, just waiting)

Open https://huggingface.co/spaces/Teja-vardhan006/speaker-count. The badge next to the name shows the stage:

- **Building:** installing packages. Click **Logs** to watch. The PyTorch download is the longest part.
- **Running:** the website is up. The very first start also downloads the speech models (about 30 s).
- **Build error** or **Runtime error:** see the troubleshooting table below.

---

## Step 5 — Test it (5 min)

1. Open **https://teja-vardhan006-speaker-count.hf.space**.
2. Upload a short clip (mp3, wav, m4a…) and click **Count speakers**. You should get the count, the timeline chart and a talk-time table.
3. Try the microphone. The browser asks for permission once.
4. Open the link on your phone with mobile data, to confirm it works off the college network.
5. At the bottom of the page, **Use via API** shows how programs (and the optional Lovable site) call `/predict`.

That's the link for your professor.

---

## Step 6 (optional) — A Lovable front-end

The Space is already a complete website.

For a second, more polished front-end, paste Prompt 1 from `deploy/LOVABLE_PROMPTS.md` into Lovable. It calls your Space through its API.

---

## Before the presentation

- **Wake the Space early.** Free Spaces sleep after a period without visitors; open the website **10 minutes before** and run one file.
- **Log in.** Logged-in Hugging Face users get a larger GPU allowance, so log in in the browser you present from.
- **Prepare clips:** 1 speaker, 2 speakers, and a 4-speaker meeting excerpt, each 2–5 minutes.
- **Limits:** 100 MB per file and 30 minutes of audio.
- **Accuracy to quote** (held-out test sets, with the same automatic speech detection the site uses):

  | Test set | Exact count | Within ±1 | Mean error |
  |---|---|---|---|
  | VoxConverse, 1–6 speakers (117 recordings) | 64 % | 86 % | 0.67 |
  | VoxConverse, all (232 recordings, 1–21 speakers) | 46 % | 64 % | 1.47 |
  | AMI meetings (16 meetings) | 69 % | 94 % | 0.38 |

  With 10 or more speakers it tends to under-count.
- **Privacy:** audio is analysed and not stored. The Space is public, so don't demo with confidential recordings.

## Troubleshooting

| What you see | Cause | Fix |
|---|---|---|
| Logs: `GatedRepoError`, `401` or `403` for `pyannote/segmentation-3.0` | Conditions not accepted, or `HF_TOKEN` missing or misnamed | Redo Step 2.1–2.2, then **Settings → Restart this Space** |
| Build error during `pip install` | A download failed, or a package version is not available there | **Settings → Factory rebuild**. If it fails on the same line again, copy ~20 log lines and ask for help |
| Error mentioning `sdk_version` or the Gradio version | The README has no or an unsupported Gradio version | Do Step 2.3, rebuild and push |
| Error mentioning ZeroGPU and the PyTorch/CUDA version | ZeroGPU does not support `torch==2.6.0` | Change `torch` and `torchaudio` in `deploy/hf_space/requirements.txt` to the version the log suggests, rebuild and push |
| "You have exceeded your GPU quota" | Daily ZeroGPU allowance used up | Log in to Hugging Face, or wait until the next day |
| `git push` says `Authentication failed` | A password was used instead of a token | GitHub: the `github_pat_…` token. Hugging Face: the **Write** token |
| Push rejected (`non-fast-forward`) | The Space already has starter files | The first time, use `git push --force space main` |
| Count looks wrong on a very short clip | Too little speech to tell voices apart | Use at least 1 minute of speech; the page warns when there is under 30 s of speech |

## Files

| Path | Purpose |
|---|---|
| `deploy/model.yaml` | Which model the site serves, its settings and measured accuracy |
| `deploy/hf_space/app.py` | Gradio page and API (`/predict`, `/model_info`); `@spaces.GPU` analysis |
| `deploy/hf_space/app_core.py` | Analysis, CPU/GPU handling, chart and texts (no Gradio code, testable anywhere) |
| `deploy/hf_space/requirements.txt`, `packages.txt`, `README.md` | What Hugging Face installs and how it runs the Space |
| `deploy/build_space.sh` | Gathers the files above plus `speakercount/` into `deploy/space_build/` |
| `deploy/hf_space_docker/` | Docker version, for paid CPU hardware or other hosts. Not used now |
| `speakercount/infer.py` | Counts speakers in one file. Test locally with `python run.py predict --audio file.mp3` |
