# Putting SpeakerCount on the web: step-by-step guide

The goal is a public website where your professor can upload an audio file and see how many people speak.
It works from any network, and the college server can stay offline.

```
Browser (any network)
   │  https://speakercount.lovable.app        ← website: built and hosted by Lovable (free)
   ▼
Lovable front-end  ── POST audio ──►  https://<hf-user>-speaker-count.hf.space   ← model: Hugging Face Space (free CPU)
                   ◄── JSON result ──   pyannote VAD → ECAPA → NME-SC graph → SpectralNet → pruning
```

Lovable can only build websites; it can't run PyTorch models. The model therefore runs on a free
Hugging Face Space, and the Lovable site calls it.

**Accounts you need (all free):**
- GitHub: https://github.com/signup
- Hugging Face: https://huggingface.co/join
- Lovable: https://lovable.dev

Do the steps in this order. Run the server commands in your SSH session on the college machine,
because the files are there. Once everything is deployed, the website no longer needs that machine.

---

## Step 1 — Put the project in your own GitHub repository

**Current state:** the project is a git repository stored only on the college server
(`/DATA/mtp2026/SpecClustering v2/.git`). It has no remote, so nothing has been uploaded anywhere yet.

**Git identity:** the commit name and e-mail configured on this server are not yours (they belong to whoever set up
the machine). The commands below set your identity **for this repository only**, so other people's settings stay as they are.

1. On github.com, create the repository:
   1. Click **+ → New repository**.
   2. Name it `speakercount-v2`.
   3. Choose **Private**. Ask your mentor before making it public.
   4. Don't add a README, .gitignore or licence; the repository must start empty.
   5. Click **Create**.
2. Create a token, which you'll use as the password when pushing:
   1. Open GitHub → **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
   2. Under *Repository access*, pick **Only select repositories** and choose `speakercount-v2`.
   3. Under *Permissions → Repository permissions*, set **Contents: Read and write**.
   4. Generate the token and copy it. GitHub shows it only once.
3. On the server:
   ```bash
   cd "/DATA/mtp2026/SpecClustering v2"
   git config user.name  "Your Name"                # this repository only
   git config user.email "your-github-email@example.com"
   git remote add origin https://github.com/<your-github-username>/speakercount-v2.git
   git push -u origin master --tags
   ```
   When git asks, enter your GitHub username, and paste the **token** as the password.
4. To upload later changes:
   ```bash
   git push
   git push --tags
   ```

**What gets uploaded** (about 17 MB): code, configs, splits, reports, the result summaries and predictions, and tuned settings.

**What stays on the server** (excluded by `.gitignore`): the datasets (AMI, VoxConverse), model checkpoints and caches.
Don't upload the datasets: they are large and have their own licences.

---

## Step 2 — Prepare Hugging Face (about 5 minutes)

1. **Token for the model, used by the server:** go to **Settings → Access Tokens → Create new token**.
   Choose type **Read** and name it `space-runtime`, then copy it.
2. **Token for uploading code:** create a second token, of type **Write**, named `push`. Copy it too.
3. **Accept the VAD model's conditions:** while logged in, open https://huggingface.co/pyannote/segmentation-3.0,
   fill in the short form and accept. Without this the server can't download the speech detector.
4. **Create the Space:**
   1. Click **+ New → Space**.
   2. Owner: you. Name: `speaker-count`.
   3. Licence: `mit`, or ask your mentor.
   4. SDK: **Docker**, template **Blank**.
   5. Hardware: **CPU basic (free)**. Visibility: **Public**.
   6. Click **Create Space**.
5. **Give the server its token:** in the Space, open **Settings → Variables and secrets → New secret**.
   Name it exactly `HF_TOKEN` and paste the **Read** token as the value.

---

## Step 3 — Deploy the model server (about 15 minutes, mostly waiting)

On the college server:

```bash
cd "/DATA/mtp2026/SpecClustering v2"
./deploy/build_space.sh                      # assembles deploy/space_build/ (code + settings only, ~300 KB)
cd deploy/space_build
git init -b main
git config user.name  "Your Name"
git config user.email "your-hf-email@example.com"
git add . && git commit -m "Speaker count API"
git remote add space https://huggingface.co/spaces/<your-hf-username>/speaker-count
git push --force space main                  # username: your HF username; password: the WRITE token
```

`--force` replaces the placeholder README that Hugging Face puts in a new Space.

Then:

1. **Wait for the build.** In the Space page, the status goes from **Building** to **Running**. The first build takes about 10–15 minutes.
   If it shows **Build error** or **Runtime error**, open the **Logs** tab and see the troubleshooting table below.
2. **Check that it's ready.** Open `https://<your-hf-username>-speaker-count.hf.space/health`.
   It should show `"status":"ready"`. Right after start-up it says `"loading"` for 1–2 minutes.
3. **Test it.** Open `https://<your-hf-username>-speaker-count.hf.space/`. That page is a small test page:
   upload an audio file and check that you get a speaker count.

This page already works as a bare-bones website by itself. If Lovable fails, you can still demo with it.

**Updating the model later** (for example with the phase-9 result):
1. Replace `deploy/tuned.yaml`, and edit `deploy/model.yaml` if needed.
2. Run `./deploy/build_space.sh` again.
3. In `deploy/space_build`, run `git add -A && git commit -m update && git push space main`.

The Lovable site doesn't change.

---

## Step 4 — Build the website with Lovable (uses 1, at most 2, of your 3 free prompts)

1. Open `deploy/LOVABLE_PROMPTS.md` and copy **Prompt 1**.
2. Replace `YOUR-HF-USERNAME` with your Hugging Face username in **lower case**. It appears once, on the `API_BASE` line.
3. In Lovable, paste it as the first message of a new project and wait until it's built.
4. Test it in the preview:
   - the status pill turns green;
   - uploading a test file shows the count, the timeline and the talk-time chart;
   - **Record** works with your microphone.
5. If something is wrong, fill in **Prompt 2** with every problem at once. Include the exact error from the browser console
   (right-click → Inspect → Console).
6. Click **Publish** (top right) to get a public link such as `https://speakercount.lovable.app`. That's the link for your professor.
7. Optional: in **Settings → GitHub**, connect it to your GitHub account. Lovable then saves the website code in its own repository,
   where you can edit text by hand (for example `src/config.ts`) without using prompts.
8. Keep **Prompt 3** for adding names, the logo and the repository link just before the presentation.

---

## Step 5 — Before the presentation

- **The free Space sleeps** after about 48 hours without use. Open the website **10 minutes before** the meeting: the status pill shows
  "Waking up", then "Server ready".
- **Have 3 test files ready.** Suggested: a 1-speaker clip, a 2-person conversation, and a 4-person meeting excerpt of 2–5 minutes.
- **Speed on the free CPU:** about 10–30 s for a 3-minute file, and a few minutes for a 30-minute file. The limits are 100 MB and 30 minutes, set in `app.py`.
- **Accuracy to quote** (held-out test sets; details in `reports/`):
  - **Oracle speech regions:**
    - 1–6 speakers on VoxConverse: 59 % exact, 84 % within ±1;
    - AMI meetings: 87.5 % exact.
  - **Automatic speech detection,** which is what the website uses: see `results/voxconverse/test_pyannote/snet_ecapa_pp/vox_tuned/summary.md`.
    It's usually a few points lower.
  - **Many speakers:** above 10 speakers the model under-counts. Say so if asked.
- **Privacy:** uploaded audio is written to a temporary folder, processed and deleted. Nothing is stored. The Space is public, so
  don't upload confidential recordings during the demo.

---

## Troubleshooting

| What you see | Cause | Fix |
|---|---|---|
| Space log: `403` or `GatedRepoError ... pyannote/segmentation-3.0` | The token's account has not accepted the model's conditions, or the secret is missing | Do Step 2.3, check the secret is named exactly `HF_TOKEN`, then **Settings → Restart Space** |
| `/health` shows `"status":"error"` | The model failed to load; the message is in `error` | Usually the same token problem; read the message |
| Space build error during `pip install` | A package download failed | Click **Factory rebuild**; if it repeats, copy the log line and ask for help |
| Website: "Failed to fetch" | Wrong `API_BASE`, or the Space is asleep or building | Open `<API_BASE>/health` in a new tab; fix `src/config.ts` (no trailing slash, lower case) |
| `413` | File larger than 100 MB | Use a shorter clip, or raise `MAX_UPLOAD_MB` in the Space settings (Variables) |
| `422 could not decode audio` | Unusual format | Convert to wav or mp3 first |
| `git push` asks for a password and then fails | A normal password was used | Paste the **token** as the password (GitHub: fine-grained token; Hugging Face: the Write token) |

## Files in `deploy/`

| File | Purpose |
|---|---|
| `model.yaml`, `tuned.yaml` | Which model the website serves, and its tuned settings |
| `hf_space/` | Server code: `app.py` (FastAPI), `Dockerfile`, `requirements.txt`, Space `README.md` |
| `build_space.sh` | Copies the code and settings into `space_build/`, ready to push |
| `LOVABLE_PROMPTS.md` | The three prompts for Lovable |

To test locally on the server:

```bash
python run.py predict --audio some_file.mp3
```

It prints the same JSON as the website's API.
