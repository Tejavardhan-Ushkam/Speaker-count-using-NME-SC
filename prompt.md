# Build prompt: Speaker-count v2 (AffinityNet + improved SpectralNet)

You are starting a **new project from scratch** in the current working directory (call it `NEW/`).
Build a complete, reproducible pipeline that **estimates the number of speakers (K) per recording**.
Train it on **AMI and VoxConverse**, test it on both, and produce plots and a `summary.md` with inferences.

> **Objective (verbatim from the owner):** "Improve the overall accuracy of the number of speakers predicted by the Siamese network + SpectralNet model."
> You may replace the Siamese network with any other model. The replacement must keep the Siamese network's useful properties (it is learned, supervised by same/different-speaker labels, and maps embeddings into a space where cosine similarity is the affinity) and must play the same role: **produce the affinity matrix** that spectral clustering consumes. SpectralNet must be kept and **improved**, not dropped.

Follow this document as the plan. Where it says "must", do it. Where it gives a choice, use the default unless an ablation step says otherwise. If something in the plan turns out to be impossible (missing data, an install that fails), stop and ask the owner instead of improvising a different plan.

---

## 0. Ground rules (read first, obey always)

1. **Old project is read-only.** The previous project lives at `/DATA/mtp2026/SpecClustering` (call it `OLD/`). You may **read** any file in it, for reference. You must **never** create, edit, move, or delete anything inside `OLD/`, and never run commands with `OLD/` as the working directory that write files (no `run.py` there, no `git` writes, no caches). Do not symlink into it for writing.
2. **Only write inside `NEW/`.** All code, configs, caches, checkpoints, results, and plots go under `NEW/`.
3. **Do not explore outside `NEW/` and `OLD/`.** Do not list or read the parent directory or any other location.
4. **Datasets are already inside `NEW/dataset/`** with the same layout as `OLD/dataset/` (see §3). Verify this at the start: count files per split and print speaker-count histograms. If anything is missing, stop and tell the owner; do not copy data from elsewhere.
5. **Environment:** Linux x86_64, Python 3.10, CUDA 12.4, GPU available. Start by copying the *content* of `OLD/requirements.txt` into `NEW/requirements.txt` (read it, write a new file). It is a locked set (torch 2.6.0+cu124, speechbrain 1.1.1, `ruamel.yaml==0.18.17` is load-bearing, pyannote.audio 3.3.2, matplotlib, scikit-learn, pyannote.metrics). **Ask the owner before installing any new package.** The only expected addition is `transformers` for the optional WavLM embedder (Phase 7); pin a version that does not upgrade torch.
6. **Never tune anything on test data.** Every threshold, every checkpoint pick, every hyperparameter is chosen on the validation sets in §3. Test sets are touched only by the final `evaluate` runs.
7. **Git:** run `git init` in `NEW/`, and commit after each phase with a clear message. Add `work*/`, `checkpoints/`, `results*/` (except final summaries and plots, see §9), and `dataset/` to `.gitignore`.
8. **Reproducibility:** fixed seeds everywhere (python, numpy, torch, k-means). Every run writes its **fully resolved config** (`config_resolved.yaml`) and the git commit hash into its results folder.

---

## 1. What the old project did (context you must understand)

Read these files in `OLD/` to understand the baseline, but **write fresh code**; do not copy files over wholesale. Small utility functions (RTTM parsing, segmentation, ECAPA embedding) may be re-implemented the same way.

| OLD file | What it does |
|---|---|
| `run.py` | CLI with `run --stages segment,embed,cluster,evaluate`, `train`, `report`, `inspect` |
| `spectralclustering/config.py` | dataclass config loaded from YAML, `--set key=value` overrides |
| `spectralclustering/segmentation.py` | 1.5 s windows, 0.75 s hop, inside each speech interval, never crossing silence; intervals shorter than 1.5 s dropped; single windows centred |
| `spectralclustering/oracle_vad.py`, `rttm.py` | oracle VAD from reference RTTM; K_true = number of distinct speakers in the RTTM |
| `spectralclustering/embedding.py` | SpeechBrain ECAPA (`speechbrain/spkrec-ecapa-voxceleb`), one L2-normalised 192-d embedding per segment |
| `spectralclustering/spectralnet/models.py` | **Siamese**: MLP 192→128→128→64, ReLU after **every** layer (including the last) |
| `spectralclustering/spectralnet/core.py` | Laplacian (`unnormalized` L=D−A or `sym_norm`); contrastive loss on **Euclidean** distance, margin 1 |
| `spectralclustering/spectralnet/train.py` | supervised pairs within each recording: label = speaker with most overlap on the window; 2 positives + 2 negatives per anchor; 30 epochs, no validation |
| `spectralclustering/spectralnet/estimate.py` | **NME-SC** (Park et al. 2020): cosine affinity (of L2-normalised Siamese outputs, or raw ECAPA), zero diagonal, row-wise top-p binarisation, symmetrise 0.5(B+Bᵀ); sweep p∈[1, 0.25·N]; for each p compute all Laplacian eigenvalues, g = max eigengap (first k_max gaps) / λ_max, r(p)=p/g; p* = argmin r; K̂ = argmax eigengap at p*; labels = k-means on first K̂ eigenvectors |
| `spectralclustering/report.py`, `metrics.py`, `plots.py` | summary.md with exact / ±1 / MAE / signed bias / relative accuracy (τ=0.15) / per-K confusion / saturation / connected components |

The original SpectralNet backend (deep spectral map with a Gaussian kNN affinity: `n_neighbors=30`, `scale_k=15`, local scale, spectral net `[128,128]+K`, minibatch training, K from eigengap of its output) was later removed from the code. Only its results remain (see below). Its leftover keys still appear in `OLD/configs/voxconverse*.yaml`.

### 1.1 Old results — AMI test (16 recordings, oracle VAD, ECAPA, 1.5 s / 0.75 s)

| Run | Method | Affinity input | Laplacian | Exact | ±1 | MAE | Mean signed error | Time |
|---|---|---|---|---|---|---|---|---|
| nmesc_ecapa_unnorm | NME-SC | raw ECAPA | unnormalized | **0.5625** | **1.00** | **0.4375** | +0.44 | 25.7 min |
| nmesc_ecapa_symnorm | NME-SC | raw ECAPA | sym_norm | 0.5000 | 1.00 | 0.5000 | +0.38 | 25.7 min |
| nmesc_siam_unnorm | NME-SC | Siamese | unnormalized | 0.2500 | 0.94 | 1.0000 | +0.75 | 7.1 min |
| nmesc_siam_symnorm | NME-SC | Siamese | sym_norm | 0.1875 | 1.00 | 0.8125 | +0.56 | 25.8 min |
| SpectralNet (two runs, "normalised" and the default; identical predictions) | SpectralNet | Siamese + Gaussian kNN | sym_norm | 0.1250 | 0.19 | 3.4375 | +3.44 | 0.1 min |

Per-recording K̂ (K_true is 4 except EN2002c = 3):

| rec | K | min | speech % | N seg | mean cos | SpectralNet | E_sym | E_unnorm | S_sym | S_unnorm |
|---|---|---|---|---|---|---|---|---|---|---|
| EN2002a | 4 | 35.7 | 88 | 2243 | 0.130 | 10 | 5 | 5 | 5 | 5 |
| EN2002b | 4 | 29.8 | 83 | 1791 | 0.141 | 7 | 5 | 4 | 5 | 5 |
| EN2002c | 3 | 49.5 | 88 | 3250 | 0.146 | 9 | 3 | 3 | 4 | 8 |
| EN2002d | 4 | 36.8 | 87 | 2333 | 0.120 | 6 | 5 | 5 | 5 | 5 |
| ES2004a | 4 | 17.5 | 75 | 928 | 0.180 | 7 | 5 | 5 | 5 | 5 |
| ES2004b | 4 | 39.1 | 86 | 2459 | 0.170 | 6 | 5 | 5 | 5 | 5 |
| ES2004c | 4 | 38.9 | 86 | 2436 | 0.149 | 9 | 4 | 4 | 5 | 5 |
| ES2004d | 4 | 37.0 | 77 | 1963 | 0.146 | 8 | 4 | 4 | 5 | 5 |
| IS1009a | 4 | 14.0 | 72 | 700 | 0.209 | 10 | 4 | 4 | 3 | 3 |
| IS1009b | 4 | 34.2 | 87 | 2216 | 0.133 | 9 | 4 | 4 | 5 | 5 |
| IS1009c | 4 | 30.3 | 83 | 1805 | 0.154 | 4 | 4 | 4 | 4 | 4 |
| IS1009d | 4 | 32.4 | 80 | 1763 | 0.171 | 9 | 4 | 4 | 3 | 3 |
| TS3003a | 4 | 25.1 | 65 | 1118 | 0.263 | 7 | 3 | 4 | 5 | 5 |
| TS3003b | 4 | 36.8 | 79 | 1991 | 0.159 | 5 | 4 | 5 | 4 | 4 |
| TS3003c | 4 | 42.8 | 70 | 2086 | 0.147 | 8 | 5 | 5 | 5 | 4 |
| TS3003d | 4 | 43.6 | 71 | 1983 | 0.170 | 4 | 5 | 5 | 4 | 4 |

Cluster sizes (% of segments, largest first) for the best run (NME-SC, raw ECAPA, unnormalized):

| rec | K̂ | sizes % | | rec | K̂ | sizes % |
|---|---|---|---|---|---|---|
| EN2002a | 5 | 39 21 18 17 **5** | | IS1009a | 4 | 69 18 8 4 |
| EN2002b | 4 | 43 25 20 13 | | IS1009b | 4 | 31 27 24 18 |
| EN2002c | 3 | 40 30 29 | | IS1009c | 4 | 38 25 22 15 |
| EN2002d | 5 | 33 25 24 11 **6** | | IS1009d | 4 | 45 37 10 8 |
| ES2004a | 5 | 44 30 14 10 **2** | | TS3003a | 4 | **90** 6 2 2 |
| ES2004b | 5 | 34 28 24 13 **1** | | TS3003b | 5 | 43 30 17 10 **0** |
| ES2004c | 4 | 38 25 20 16 | | TS3003c | 5 | 37 27 23 12 **1** |
| ES2004d | 4 | 34 32 28 7 | | TS3003d | 5 | 57 16 13 12 **2** |

With the Siamese affinity, the extra cluster is **not** tiny: the smallest of 5 clusters is 10–16 % of segments (for example ES2004c: 25 24 18 17 16). So the Siamese space genuinely splits one speaker in two.

No VoxConverse results exist in the old project. You will produce them.

### 1.2 Inferences from the old results

1. **The AMI test set barely tells methods apart.** Reference K per split: AMI train 136 recordings (K=3:4, K=4:129, K=5:3); AMI dev 18 (all K=4); AMI test 16 (K=3:1, K=4:15). Always answering "4" scores 93.8 % exact on AMI test, better than every old method. VoxConverse (K from 1 to 21) is where counting ability is really measured. Always report the "predict the training mode" baseline.
2. The best old setup is raw ECAPA + NME-SC with the unnormalized Laplacian. All of its errors are +1 overestimates.
3. The Siamese network made things worse (exact accuracy 0.56 → 0.19–0.25) and pushes K̂ to 5.
4. SpectralNet was unusable: +3.4 average overestimate, and K̂ hit k_max=10 on EN2002a and IS1009a.
5. The "normalised" SpectralNet run produced exactly the same K̂ as the default run, so whatever it changed had no effect, and nobody noticed. The resolved config was not saved with the results.

### 1.3 Failure modes you must design against

| ID | Failure | Evidence | Root cause | Your countermeasure |
|---|---|---|---|---|
| A | Tiny extra cluster | ES2004a/b, TS3003b/c/d: 5th cluster 0–2 % | overlapped speech, laughter, noise, backchannels | overlap-aware labels (§4.2), cluster pruning tuned on val (§4.6) |
| B | One speaker split into two | EN2002a/d (5–6 %), every Siamese +1; for EN2002a/d the 2nd-best eigengap is at 4, with a top/second gap ratio of 1.4–1.7 | drift over a 30–50 min meeting; each segment embedded with no session context | session-level AffinityNet with time encoding (§4.3), centroid merge (§4.6) |
| C | Right K, wrong clusters | TS3003a sizes 90 6 2 2; highest mean cosine 0.263; lowest speech fraction 65 % | one dominant cluster swallows others | report DER and cluster health, not just K |
| D | Saturation / no clear eigengap | SpectralNet K̂ = k_max | minibatch SpectralNet with a fixed Gaussian kNN affinity has no clean spectrum | full-batch SpectralNet on the learned affinity, verified against exact eigenvalues (§4.5) |
| E | Very slow | ~25 min for 16 recordings | full `eigvalsh` for every p up to 0.25·N (≈800 decompositions of 3250×3250) | `p_max_abs` (default 60) plus coarse-to-fine p search (§4.4) |
| F | Silent no-op experiments | "normalised" = default | config not saved; no comparison check | `config_resolved.yaml` per run; warn when two runs give identical K̂ (§6) |

### 1.4 Code flaws of the old Siamese network (must not be repeated)

1. **ReLU on the output layer** (`OLD/spectralclustering/spectralnet/models.py` lines 17–19). Outputs are ≥ 0, so every cosine is ≥ 0 and the angular space is squeezed into one orthant.
2. **Metric mismatch.** Training uses contrastive loss on raw Euclidean distance (`core.py` 23–27); inference uses cosine of L2-normalised outputs (`estimate.py` 95–96).
3. **192-d ECAPA squeezed into 64-d** by an MLP trained on about 136 meetings. This throws away information learned from thousands of VoxCeleb speakers.
4. **Weak and noisy supervision.** Only 2 positive and 2 negative pairs per anchor, random negatives, and labels taken from the speaker with most overlap, so overlapped windows are mislabelled (`train.py` 29–59).
5. **No session context.** Each segment is embedded on its own, so drift within a meeting can't be corrected.
6. **No validation or early stopping.** Fixed 30 epochs.
7. **SpectralNet's K comes from the network's own output spectrum**, with minibatch orthogonalisation and a fixed Gaussian kNN affinity. Its eigengap is not a reliable count.

---

## 2. What you are building (overview)

```
audio ──► VAD (oracle default | pyannote) ──► 1.5 s/0.75 s segments ──► ECAPA 192-d (cached)
                                                                              │
                                     ┌────────────────────────────────────────┘
                                     ▼
                     AffinityNet (replaces Siamese; session-level Transformer,
                                  residual over ECAPA, cosine output, no final ReLU)
                                     │  refined embeddings z (L2-normalised)
                                     ▼
                     affinity A = cos(z_i, z_j)  ──► optional refinement ops
                                     │
                                     ▼
                     NME-SC p* search (fast) ──► sparse affinity W at p*
                                     │
              ┌──────────────────────┴──────────────────────┐
              ▼                                             ▼
   exact backend: eigh(L(W))                     SpectralNet v2 (full-batch, orthonormal
                                                 output, trained on W; Ritz eigenvalues)
              │                                             │
              └──────────────► eigengap K̂ ◄─────────────────┘
                                     │
                                     ▼
                     k-means labels ──► post-processing: prune tiny clusters,
                                        merge near-duplicate centroids ──► final K̂, labels
                                     │
                                     ▼
                     evaluate: count metrics, DER, cluster health, plots, summary.md
```

Methods to compare (each one is a named `method` preset in config):

| Method id | Affinity | Count backend | Post-processing |
|---|---|---|---|
| `baseline_mode` | — | always predict the most common K in that dataset's training split | — |
| `nmesc_ecapa` | raw ECAPA cosine | exact eigh | none (this reproduces the old best; must match §1.1 on AMI test to within ±1 recording) |
| `nmesc_ecapa_pp` | raw ECAPA cosine | exact eigh | prune + merge |
| `nmesc_affnet` | AffinityNet | exact eigh | none |
| `nmesc_affnet_pp` | AffinityNet | exact eigh | prune + merge |
| `snet_affnet_pp` | AffinityNet | **SpectralNet v2** | prune + merge (**main proposed system**) |
| `snet_ecapa_pp` | raw ECAPA | SpectralNet v2 | prune + merge (shows how much the improved SpectralNet alone helps) |

---

## 3. Data and splits

Layout inside `NEW/dataset/` (same as the old project; verify it):

| Corpus | Audio | RTTM |
|---|---|---|
| AMI train / dev / test | `dataset/train`, `dataset/dev`, `dataset/test` (`{rec}.wav`) | `dataset/rttms/train`, `dataset/rttms/dev`, `dataset/rttms/test` |
| VoxConverse dev / test | `dataset/voxconverse/audio/dev`, `dataset/voxconverse/audio/test` | `dataset/voxconverse/rttm/dev`, `dataset/voxconverse/rttm/test` |

Splits used by this project:

| Role | AMI | VoxConverse |
|---|---|---|
| **train** (AffinityNet) | AMI train (136) | VoxConverse dev, 80 % of recordings |
| **val** (early stopping, all tuning) | AMI dev (18) | VoxConverse dev, the other 20 % |
| **test** (final numbers only) | AMI test (16) | VoxConverse test |

- Make the VoxConverse 80/20 split **by recording**, stratified by K bins (1, 2, 3–4, 5–7, 8+), seed 0. Save it to `NEW/splits/voxconverse_{train,val}.txt` and commit it.
- AMI dev is all K=4, so on its own it can't tune counting thresholds well. Tune post-processing thresholds on **both val sets jointly** (objective in §4.6).
- `k_max`: AMI 10, VoxConverse 25 (the old config used 21 because one test recording, `nitgx`, has 21 speakers; 25 leaves headroom).

---

## 4. Components (implementation detail)

### 4.1 Segmentation and embeddings (same as old, cached)

- Oracle VAD from the RTTM by default (union of all turns); a `pyannote/segmentation-3.0` VAD option for the realistic setting (`vad.source: pyannote`).
- Windows of 1.5 s with 0.75 s hop inside each speech interval; drop intervals < 1.5 s; centre single windows.
- ECAPA `speechbrain/spkrec-ecapa-voxceleb`, batch 128, L2-normalised 192-d. Cache to `work/<dataset>/<split>/embeddings/{rec}.npy`, and segments plus metadata to `.../segments/{rec}.json`.
- Store per segment: start, end, interval index, centre time (seconds), and (train/val only) the label info from §4.2.

### 4.2 Overlap-aware segment labels (training and analysis only)

For each window, compute how many seconds each reference speaker is active inside it.
- **clean**: one speaker covers ≥ 90 % of the window **and** every other speaker covers ≤ 10 %. Label = that speaker.
- **overlap/ambiguous**: anything else. Label = `None`.

Ambiguous segments are **still passed** to AffinityNet as context tokens, but are **masked out of the loss**. Report the fraction of ambiguous segments per dataset in the data summary.

Never use RTTM labels or overlap information at inference in the main methods. An "oracle overlap removal" variant (drop ambiguous segments before counting) is allowed **only** as a clearly labelled ablation (§7), to measure how much overlap hurts.

### 4.3 AffinityNet (replaces the Siamese network)

Purpose: same as the Siamese network (learned, supervised by same/different speaker, cosine affinity) but without flaws 1–6 from §1.4.

Architecture (PyTorch, `NEW/speakercount/affinity/model.py`):
- Input: ECAPA x ∈ ℝ^{N×192} for one session (or a chunk of it), plus centre times t ∈ ℝ^N.
- `h0 = Linear(192→256)(x) + TimeEncoding(t)`. TimeEncoding is sinusoidal over **seconds** (periods from 1 s to 4000 s), projected to 256.
- 4 Transformer encoder layers, d_model 256, 4 heads, FFN 1024, dropout 0.1, pre-LayerNorm, `batch_first=True`, PyTorch SDPA attention.
- Output head `Linear(256→192)` with **no activation**.
- **Residual over ECAPA:** `z = normalize(x + α · head(h))`, α a learnable scalar initialised at 0.1. At initialisation AffinityNet ≈ raw ECAPA, so it can't start worse than the baseline.
- Affinity at inference: `A = z zᵀ` (cosine), diagonal set to 0.

Loss (`NEW/speakercount/affinity/loss.py`), computed on clean segments only:
- **Pairwise logistic loss on all pairs** in the chunk: `s_ij = w · cos(z_i, z_j) + b` with learnable w (init 10, kept positive via softplus) and b (init −5); target 1 for same speaker, 0 otherwise. BCE with `pos_weight` = (#neg / #pos) in that chunk. Using all pairs gives hard negatives automatically.
- Plus **supervised contrastive (SupCon)** loss, temperature 0.1, weight 0.5.
- This trains and evaluates **the same metric (cosine)**, fixing flaw 2.

Training data sampling (`NEW/speakercount/affinity/data.py`):
- Each example is a **chunk of consecutive segments** from one session: random length 256–1024 (whole session if shorter), random start.
- **Speaker-dropout augmentation (on by default, p=0.5):** remove all segments of a random subset of speakers (keep at least 1). This creates K=1..4 examples from AMI, so the model doesn't learn "there are always 4".
- Embedding noise: Gaussian noise σ=0.01 then re-normalise; random segment dropout 10 %.
- Balance corpora: each batch draws AMI and VoxConverse chunks 50/50. Batch = 8 chunks (pad and mask).
- Optional (ablation only) **session mixing:** concatenate chunks from 2 sessions of the *same* corpus to create larger K. Off by default; channel differences may make this too easy.

Optimisation: AdamW, lr 3e-4, weight decay 0.01, 1000 warm-up steps then cosine decay, gradient clipping 1.0, mixed precision (bf16 if supported), at most 60 epochs (define an epoch as one pass over training sessions × 4 chunks).

Validation every epoch, on both val sets:
- pairwise EER of the cosine affinity on clean pairs (subsample to ≤ 200k pairs per recording);
- **count metrics** from running the full `nmesc_affnet` pipeline (exact backend, no post-processing).

**Model selection metric:** `val_score = 0.5 · MAE_AMI-dev + 0.5 · mean_relative_error_Vox-val`. Keep the best checkpoint by `val_score`; stop early after 8 epochs without improvement. Save `checkpoints/affnet/best.pt`, `last.pt`, and `train_log.csv` (epoch, losses, EER, count metrics, lr).

Inference: run the full session in one forward pass (N ≤ ~6000 fits with SDPA in bf16). If it runs out of memory, process overlapping chunks of 2048 segments with a stride of 1024, average z over the overlaps, and re-normalise. Write a unit test that both paths give nearly the same z on a session that fits.

### 4.4 NME-SC, fast version (`NEW/speakercount/cluster/nmesc.py`)

Same algorithm as the old project (§1), with these changes:
- `p_max = min(floor(0.25·N), p_max_abs)`, with `p_max_abs` default **60**. Log p* per recording and plot its distribution; if p* often equals p_max_abs, raise it.
- **Coarse-to-fine search:** evaluate p on a stride-4 grid, then stride 1 within ±4 of the best coarse p.
- During the search, compute only the **smallest k_max+1 eigenvalues** (`torch.lobpcg` or `scipy.sparse.linalg.eigsh` on the sparse Laplacian, which=SM via shift-invert); fall back to dense `eigvalsh` if it fails to converge. Unit-test that both give the same p* and K̂ on 3 recordings.
- Laplacian: `unnormalized` by default (best in the old results); `sym_norm` as an ablation.
- Save in each recording's `.npz`: `k_pred`, `k_eigengap` (before post-processing), `p_star`, `r_values`, `eigenvalues[:k_max+5]`, `eigengaps`, `gap_ratio` (top gap / second gap), `second_best_k`, `labels`, `cluster_sizes`, `n_components`, `mean_cosine`, timings.

Target: AMI test clustering time ≤ 3 min total (old: 25 min).

### 4.5 SpectralNet v2 — the improved SpectralNet (`NEW/speakercount/cluster/spectralnet.py`)

SpectralNet (Shaham et al., ICLR 2018) learns a map f: z → y ∈ ℝ^m whose outputs are orthonormal and minimise the Laplacian energy, so y approximates the bottom eigenvectors of L. Fix what broke it before:

1. **Input and affinity:** input = AffinityNet embeddings z (or raw ECAPA for `snet_ecapa_pp`). The affinity W is the **NME-SC sparse affinity at p*** from §4.4, not a fixed Gaussian kNN with `n_neighbors=30`.
2. **Full-batch training per session.** N ≤ ~6000, so use all segments in each step. This removes the minibatch orthogonalisation error that made the old spectrum useless.
3. **Network:** MLP 192→256→256→m with ReLU on the hidden layers and a **linear output**, m = k_max + 1. Then an **orthonormalisation layer**: Y = Ỹ · (Lchol⁻¹)ᵀ · √N, where Lchol is the Cholesky factor of ỸᵀỸ (add 1e-6·I jitter). During training, recompute the factor each step from the full batch; freeze it for inference.
4. **Loss:** `trace(Yᵀ L Y) / N`, with L the same Laplacian type as NME-SC. Adam, lr 1e-3, at most 500 full-batch steps, stop when the relative loss change is < 1e-5 for 20 steps. Seed fixed.
5. **Eigenvalues via Rayleigh–Ritz:** form M = Yᵀ L Y / N (m×m), take its eigen-decomposition → Ritz values λ̂₁ ≤ … ≤ λ̂_m and rotate Y by M's eigenvectors. K̂ = argmax eigengap of the Ritz values over the first k_max gaps (same rule as NME-SC).
6. **Self-check (must be logged per recording):** compare the Ritz values with exact `eigvalsh` of L for the first k_max+1 values. Report the max relative error and whether K̂ from SpectralNet equals K̂ from the exact backend. Put an "agreement rate" in summary.md. If agreement < 90 % on val, flag it in the summary and investigate before claiming any SpectralNet result.
7. **Labels:** k-means (n_init 10) on the first K̂ rotated columns of Y, rows L2-normalised.
8. **Warm start (optional, on by default):** initialise each session's SpectralNet from a network pre-trained on the training sessions (same objective, 50 steps per session, random order). Report fit time with and without the warm start.

Why this is still SpectralNet and not just eigh: it gives a parametric map, so new segments from the same session can be embedded and labelled without recomputing the eigen-decomposition (test this on 10 % held-out segments of 3 val recordings: label agreement with the full run ≥ 95 %).

### 4.6 Post-processing (`NEW/speakercount/cluster/postprocess.py`)

Applied after any backend, in this order:
1. **Prune tiny clusters:** clusters whose share of segments is < `min_cluster_share` are dissolved; their segments are re-assigned to the nearest remaining centroid (cosine on z). K̂ decreases accordingly.
2. **Merge near-duplicate clusters:** while the highest centroid cosine between two clusters > `merge_threshold`, merge those two and recompute centroids.
3. Never go below K̂ = 1.
4. **Single-speaker check (VoxConverse has K=1 recordings):** if the mean off-diagonal cosine > `single_speaker_threshold`, set K̂ = 1. Tune this as well; it may end up disabled.

Tuning (`run.py tune`): grid search on the **val sets only**.
- `min_cluster_share` ∈ {0, 0.01, 0.02, 0.03, 0.05, 0.07}
- `merge_threshold` ∈ {off, 0.5, 0.6, 0.7, 0.8}
- `single_speaker_threshold` ∈ {off, 0.5, 0.6, 0.7}
- Objective: `0.5 · exact_AMI-dev + 0.5 · relative_accuracy_Vox-val`, ties broken by lower MAE.
- Tune separately for each method that uses post-processing. Save `results/tuning/<method>.csv` (every grid point) and `best.yaml`. Expect pruning to reduce AMI +1 errors but possibly hurt recordings with one dominant speaker (old TS3003a: 90/6/2/2); the plots must show this trade-off.

### 4.7 Optional refinement ops (ablation, off by default)

The affinity refinement sequence from Wang et al. 2018 ("Speaker diarization with LSTM"): Gaussian blur (σ=1 along the time-ordered matrix), row-wise thresholding (keep top 95th percentile per row, multiply the rest by 0.01), symmetrisation (max), diffusion (A·Aᵀ), row-max normalisation. Apply it before NME-SC when `affinity.refine: true`.

---

## 5. Evaluation (`NEW/speakercount/eval/`)

For every (method, dataset, split) run, write `results/<dataset>/<split>/<method>/`:
- `predictions.csv`: recording_id, k_true, k_pred, k_eigengap (before post-processing), p_star, gap_ratio, second_best_k, smallest_cluster_share, largest_cluster_share, n_segments, n_ambiguous_segments, mean_cosine, saturated, duration_sec, speech_sec, cluster_sec, der, der_no_overlap, snet_exact_agree (SpectralNet methods only).
- `config_resolved.yaml`, `git_commit.txt`.
- `hyp_rttm/{rec}.rttm`: hypothesis RTTM built from segment labels (assign each frame to the label of the segment whose centre is nearest; merge consecutive equal labels).

Metrics:
- Counting: exact, ±1, MAE, mean signed error, relative accuracy (τ=0.15), mean and median relative error, **per-K-bin** breakdown (bins 1, 2, 3, 4, 5–7, 8–12, 13+), confusion matrix.
- **DER** with `pyannote.metrics` DiarizationErrorRate, collar 0.25 s; report both `skip_overlap=False` and `skip_overlap=True`. With oracle VAD, the missed-speech part comes only from overlap; say so.
- **Cluster health:** number of recordings with smallest cluster < 3 %, largest cluster > 80 %, K̂ = k_max, gap_ratio < 1.5.
- **Statistics vs `nmesc_ecapa`:** paired bootstrap (10 000 resamples over recordings) 95 % CI for the difference in MAE and in exact accuracy; Wilcoxon signed-rank test on |K̂−K|. Report p-values. On AMI test (n=16) state that the power is low.
- **Baselines must always appear next to the proposed numbers:** `baseline_mode` and `nmesc_ecapa`.

---

## 6. Reports and plots

### 6.1 Per-run `summary.md` (`run.py report`)
Same structure as the old reports (config table, accuracy, relative accuracy, confusion, per-K breakdown, notes), plus: DER table, cluster-health table, SpectralNet agreement rate, p* distribution (median, max, how often it hits p_max_abs), timing, the comparison against both baselines with bootstrap CIs, and a list of the 5 worst recordings with K, K̂, cluster sizes and gap_ratio.

### 6.2 Final cross-method `results/SUMMARY.md` (`run.py compare`)
1. One headline table per dataset (AMI test, VoxConverse test): every method in §2 × {exact, ±1, MAE, signed error, relative accuracy, DER}. Bold the best value in each column.
2. Validation table: same metrics on AMI dev and Vox-val, plus the tuned post-processing values.
3. Ablation table (§7).
4. **Inferences:** written by you from the numbers, not boilerplate. At minimum answer:
   - Did AffinityNet beat raw ECAPA, and on which failure modes (A/B/C/D from §1.3)? Give recording ids.
   - Did SpectralNet v2 match the exact backend (agreement rate), and did it add anything (speed, out-of-sample)?
   - How much did post-processing help, and where did it hurt?
   - How does the error depend on true K (VoxConverse)? Where does it break down?
   - Does the gain hold with pyannote VAD instead of oracle VAD?
   - Is the AMI improvement statistically meaningful given n=16 and the 93.8 % mode baseline?
5. **Failure analysis:** remaining failure modes, with example recordings and which plot shows them.
6. **Next steps:** concrete, ranked.
7. A warning line if any two methods produced identical K̂ on every recording of a split (catch silent no-ops like the old "normalised" run).

### 6.3 Plots (`run.py plots`, matplotlib, PNG at 150 dpi plus PDF, saved under `results/plots/`)

Use a consistent colour for each method across all plots, readable axis labels, titles with dataset/split, and colourblind-safe colours (e.g. matplotlib `tab10` in a fixed order). Every figure must be referenced from SUMMARY.md with a one-line caption saying what to look at.

1. `metrics_bar_<dataset>.png`: exact / ±1 / MAE per method with bootstrap 95 % CI error bars, baselines included.
2. `confusion_<dataset>_<method>.png`: true K vs K̂ heatmap, with counts annotated.
3. `error_hist_<dataset>.png`: histogram of K̂−K per method (small multiples).
4. `scatter_k_<dataset>.png`: K̂ vs K with jitter and the y=x line (VoxConverse is the important one).
5. `error_vs_k_vox.png`: MAE and relative error per K-bin, one line per method.
6. `affinity_<rec>.png`: affinity matrices side by side (raw ECAPA vs AffinityNet), rows/cols sorted by reference speaker, then time; speaker boundaries drawn. Do this for 2 best and 2 worst recordings per test set, including AMI EN2002a and TS3003a.
7. `spectrum_<rec>.png`: first k_max+3 eigenvalues and eigengaps, exact vs SpectralNet Ritz values overlaid, true K and K̂ marked.
8. `cluster_shares_<dataset>.png`: smallest-cluster share for correct vs wrong recordings, per method (strip or box plot), with the tuned `min_cluster_share` drawn as a line.
9. `tuning_heatmap_<method>.png`: val objective over `min_cluster_share` × `merge_threshold`.
10. `train_curves.png`: training loss, val pair EER, val count MAE and val_score per epoch, with the chosen epoch marked.
11. `tsne_<rec>.png`: t-SNE (sklearn) of raw ECAPA vs AffinityNet embeddings for one AMI and one VoxConverse recording, coloured by reference speaker, ambiguous segments in grey.
12. `pstar_hist.png`: p* distribution per dataset, with p_max_abs marked.
13. `der_bar_<dataset>.png`: DER per method (with and without overlap).
14. `timing.png`: clustering time per recording vs N, exact vs SpectralNet vs old (25.7 min / 16 recordings) reference.

---

## 7. Ablations (run on val, plus test for the final table)

| Ablation | Compare |
|---|---|
| Laplacian | unnormalized vs sym_norm |
| AffinityNet context | full Transformer vs the same model with 0 layers (residual MLP only, like a fixed Siamese) |
| Time encoding | on vs off |
| Speaker-dropout augmentation | on vs off |
| Training corpora | AMI only vs Vox only vs both |
| Loss | BCE only vs BCE + SupCon |
| Overlap handling | clean-only loss (default) vs most-overlap labels like the old project |
| Oracle overlap removal at inference | off (default) vs on (**labelled as oracle, upper bound only**) |
| Refinement ops | off vs on |
| SpectralNet warm start | on vs off |
| VAD | oracle vs pyannote/segmentation-3.0 |
| Old Siamese, re-implemented with flaws 1–2 fixed only | to show how much those two bugs cost |

---

## 8. Project layout and CLI

```
NEW/
  run.py                      # single CLI entry point
  requirements.txt
  configs/
    base.yaml                 # shared defaults
    ami_{train,dev,test}.yaml
    vox_{train,val,test}.yaml           # train/val read splits/voxconverse_*.txt
    vox_test_pyannote.yaml, ami_test_pyannote.yaml
    affnet_train.yaml         # lists train + val configs, model + optimiser
    methods/<method>.yaml     # presets from §2
  splits/voxconverse_{train,val}.txt
  speakercount/
    config.py  rttm.py  vad.py  segmentation.py  embedding.py  labels.py
    affinity/{model.py, loss.py, data.py, train.py, infer.py}
    cluster/{laplacian.py, nmesc.py, spectralnet.py, postprocess.py, kmeans.py}
    eval/{metrics.py, der.py, stats.py, report.py, compare.py, plots.py}
    pipeline.py
  tests/                      # pytest
  scripts/run_all.sh          # the full sequence in §8.2
  work/  checkpoints/  results/
  README.md
```

### 8.1 CLI (implement exactly these subcommands)

```
python run.py check-data                                    # verify dataset layout, K histograms, write results/data_summary.md
python run.py make-splits                                   # VoxConverse 80/20 stratified split
python run.py prepare  --config configs/ami_train.yaml      # segment + embed (+ labels) ; cached, --force to redo
python run.py train-affnet --config configs/affnet_train.yaml [--set key=value ...]
python run.py cluster  --config configs/ami_dev.yaml --method nmesc_affnet_pp [--only REC ...] [--force]
python run.py tune     --method nmesc_affnet_pp            # grid search on AMI dev + Vox val
python run.py evaluate --config configs/ami_test.yaml --method snet_affnet_pp
python run.py report   --config configs/ami_test.yaml --method snet_affnet_pp
python run.py compare                                      # writes results/SUMMARY.md
python run.py plots                                        # writes results/plots/*
python run.py inspect  --config configs/ami_test.yaml --method snet_affnet_pp --recording EN2002a
```

Every subcommand supports `--set dotted.key=value`. Each run writes into `results/<dataset>/<split>/<method>[/<tag>]` and never overwrites another method's folder.

### 8.2 `scripts/run_all.sh` (end-to-end, in this order)

```
python run.py check-data
python run.py make-splits
for c in ami_train ami_dev ami_test vox_train vox_val vox_test; do python run.py prepare --config configs/$c.yaml; done
python run.py train-affnet --config configs/affnet_train.yaml
for m in nmesc_ecapa_pp nmesc_affnet_pp snet_affnet_pp snet_ecapa_pp; do python run.py tune --method $m; done
for c in ami_test vox_test; do
  for m in baseline_mode nmesc_ecapa nmesc_ecapa_pp nmesc_affnet nmesc_affnet_pp snet_affnet_pp snet_ecapa_pp; do
    python run.py evaluate --config configs/$c.yaml --method $m
  done
done
# realistic VAD
for c in ami_test_pyannote vox_test_pyannote; do python run.py prepare --config configs/$c.yaml; \
  for m in nmesc_ecapa snet_affnet_pp; do python run.py evaluate --config configs/$c.yaml --method $m; done; done
python run.py compare
python run.py plots
```

Also list these commands, with expected run times, in `README.md`.

---

## 9. Phases (do them in order; commit after each; report to the owner at each checkpoint ✅)

**Phase 0 — Setup.** `git init`, `.gitignore`, `requirements.txt`, package skeleton, config loader with `--set`, `check-data`, `make-splits`. ✅ Show the data summary (files and K histogram per split, ambiguous-segment fraction comes in Phase 1).

**Phase 1 — Data pipeline.** RTTM, oracle VAD, segmentation, ECAPA embedding, overlap-aware labels, `prepare`. Tests: segmentation matches the old rules (compare segment counts for 2 AMI test recordings with the old table: EN2002a 2243, IS1009a 700). ✅ Report segment and ambiguous counts.

**Phase 2 — Baseline reproduction.** Fast NME-SC + exact backend + `baseline_mode` + `nmesc_ecapa` + evaluation + report. ✅ AMI test `nmesc_ecapa` must reproduce the old 9/16 exact (±1 recording) while the clustering time drops to ≤ 3 min. If it doesn't match, find out why before going on (p_max_abs is the first suspect; compare to the old p* by running with `p_max_abs: null`). Also produce the first VoxConverse test baseline numbers.

**Phase 3 — Post-processing + tuning** on `nmesc_ecapa_pp`. ✅ Report val gains and the tuned values.

**Phase 4 — AffinityNet.** Model, loss, sampler, training with early stopping, inference, `nmesc_affnet(_pp)`. ✅ Report training curves and val metrics vs `nmesc_ecapa_pp`. If AffinityNet does not beat raw ECAPA on val_score, try at most these, in order: lower lr (1e-4); α init 0.05; 2 layers instead of 4; turn session mixing on. Then report honestly.

**Phase 5 — SpectralNet v2.** Implementation, self-check against exact, warm start, out-of-sample test, `snet_*_pp`. ✅ Report agreement rate and timing.

**Phase 6 — Final evaluation + ablations + pyannote VAD.**

**Phase 7 (optional, ask the owner first) — WavLM embedder.** `microsoft/wavlm-base-plus-sv` via `transformers` as an alternative to ECAPA (512-d; AffinityNet input dim from config). Only if Phases 0–6 are done.

**Phase 8 — Reports.** `compare`, `plots`, final `results/SUMMARY.md` with inferences, failure analysis and next steps. Commit summaries and plots (allow `results/**/summary.md`, `results/SUMMARY.md`, `results/plots/**`, `results/**/predictions.csv` in `.gitignore`).

---

## 10. Success criteria (targets, not guarantees; report honestly either way)

| Dataset | Metric | Old best (`nmesc_ecapa`) | Target for `snet_affnet_pp` |
|---|---|---|---|
| AMI test | exact | 0.5625 | ≥ 0.80, **and** compare against the 0.9375 "always 4" baseline |
| AMI test | MAE | 0.4375 | ≤ 0.25 |
| VoxConverse test | MAE and relative accuracy | measure in Phase 2 | ≥ 20 % relative MAE reduction vs `nmesc_ecapa`, bootstrap CI excluding 0 |
| both | SpectralNet vs exact K̂ agreement | — | ≥ 90 % |
| both | K̂ = k_max saturations | 2/16 (SpectralNet) | 0 |
| AMI test | clustering time | 25.7 min | ≤ 3 min |

If a target is missed, say so in SUMMARY.md, show which failure mode is responsible, and propose the next fix. Do not change test-time choices to hit a target.

---

## 11. Pitfalls and tips

- Speaker IDs are only meaningful **within** a recording (VoxConverse uses `spk00`, `spk01`, … per file). Build pair labels within a session only.
- Pad and mask variable-length chunks in batches. Masked tokens must not enter attention or the loss.
- Keep AffinityNet's affinity **cosine of L2-normalised z** everywhere: training, validation, inference, and SpectralNet input.
- Zero the affinity diagonal before binarisation (the old code did this; keep it).
- Use float64 for eigen-decompositions in tests; float32 is fine in production but check that K̂ is the same on 3 recordings.
- Long VoxConverse files can exceed 6000 segments. Watch GPU memory in AffinityNet inference, the dense Laplacian, and SpectralNet; use the chunked path or sparse eigsh when N is large.
- `k_max` must be ≥ the largest true K in that dataset (check in `check-data`).
- Record wall time for every stage.
- Unit tests (pytest) at minimum: segmentation rules; overlap labels on a synthetic RTTM; NME-SC on a synthetic block-diagonal affinity with known K (2, 4, 7); dense vs sparse eigen agreement; SpectralNet Ritz values vs eigh on a synthetic graph (relative error < 1e-2); post-processing prune and merge on toy clusters; DER = 0 for a hypothesis equal to the reference; chunked vs full AffinityNet inference.
- Never print or log the owner's personal details. No network calls other than downloading the pretrained models from Hugging Face (ECAPA, pyannote segmentation, and optionally WavLM).
