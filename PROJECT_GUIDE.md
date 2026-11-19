# Speaker Counting with AffinityNet and SpectralNet v2: Project Guide

This document explains the whole project: the problem, the research questions, how the system works, every phase and
experiment that was run, the results, and what they mean. It assumes basic machine learning knowledge but no prior
knowledge of this codebase. After reading it you should be able to present and defend the project.

Other documents in the repository:
- [`results/SUMMARY.md`](results/SUMMARY.md) has the complete auto-generated numeric tables.
- [`results/plots/captions.md`](results/plots/captions.md) explains every figure.
- [`README.md`](README.md) has the commands.
- [`prompt.md`](prompt.md) is the original build plan.

Git tags that freeze each stage:
- `ami-only-v1`: everything trained, tuned and tested on AMI.
- `vox-crosscorpus-v1`: the same models evaluated on VoxConverse.

---

## 1. The problem in one paragraph

Given a recording of a conversation, **how many different people speak in it?** This is *speaker counting*. It is the
first step of *speaker diarization* ("who spoke when"), because the system must decide the number of speakers K before it
can assign each stretch of speech to one of them. If K is wrong, the diarization is wrong, whatever else the system does.

The standard approach is unsupervised:
1. Cut the speech into short windows.
2. Turn each window into a speaker embedding (a vector that is similar for the same voice).
3. Build a similarity graph between the windows.
4. Use *spectral clustering* to find how many well-separated groups the graph has.

This project tries to make that count more accurate and faster, using two learned components.

---

## 2. Background concepts (needed to follow the rest)

| Term | Meaning |
|---|---|
| **VAD** (voice activity detection) | Finds where speech is. *Oracle VAD* takes it from the human reference annotation, which gives an upper bound and isolates the clustering problem. *pyannote VAD* is a real neural VAD (`pyannote/segmentation-3.0`), the realistic setting. |
| **Segment / window** | A 1.5 s piece of speech. Windows start every 0.75 s (50 % overlap) and never cross a silence. A 40-minute meeting gives about 2 000–3 000 segments. |
| **ECAPA-TDNN** | A pretrained speaker-embedding network (SpeechBrain, trained on VoxCeleb). Each segment becomes a 192-dimensional unit vector. Two segments of the same voice should have high cosine similarity. |
| **RTTM** | The standard annotation file: one line per speaker turn (recording, start, duration, speaker). The true K is the number of distinct speakers in it. |
| **Affinity matrix A** | An N×N matrix of pairwise cosine similarities between segments. |
| **Graph Laplacian L** | L = D − W, where W is the (sparsified) affinity and D is the diagonal degree matrix. If the graph has K well-separated groups, L has K eigenvalues near 0 and then a jump. |
| **Eigengap** | The jump λ_{k+1} − λ_k between consecutive sorted eigenvalues. The estimate K̂ is the k with the largest gap. |
| **NME-SC** | *Normalized Maximum Eigengap Spectral Clustering* (Park et al., 2020). It binarises the affinity by keeping each row's top-p neighbours. It picks p automatically by minimising p / (normalised max eigengap), then reads K̂ from the eigengap at that p\*. It needs no tuned threshold. |
| **k-means on eigenvectors** | After K̂ is known, the segments are labelled by k-means on the first K̂ eigenvectors. This gives the clusters (who spoke when). |
| **SpectralNet** | Shaham et al., 2018. A neural network trained so that its outputs behave like the bottom eigenvectors of L, giving a *parametric* spectral embedding. |
| **DER** (diarization error rate) | The share of speech time attributed to the wrong speaker, or missed, or falsely detected. It measures cluster quality, not just the count. |
| **Exact accuracy / ±1 / MAE** | The share of recordings with K̂ = K, the share with \|K̂ − K\| ≤ 1, and the mean \|K̂ − K\|. *Signed error* is the mean (K̂ − K): positive means overcounting. *Relative accuracy* is the share of recordings with \|K̂ − K\|/K ≤ 0.15. |

---

## 3. Starting point: the old project and why it needed a v2

An earlier project (the "old" folder, which was only read) built the standard pipeline above and tried two learned
additions. Its results on AMI test (16 meetings) were:

| Old method | Exact | MAE | Time |
|---|---|---|---|
| NME-SC on raw ECAPA (best) | 0.5625 | 0.4375 | 25.7 min |
| NME-SC on a Siamese network's embeddings | 0.19–0.25 | 0.81–1.00 | 7–26 min |
| SpectralNet | 0.125 | 3.44 | 0.1 min |
| **"Always say 4"** (no model) | **0.9375** | 0.0625 | – |

The last row is the key fact. On AMI, 15 of the 16 test meetings have exactly 4 speakers. A constant guess beats every
model, so AMI on its own cannot show real counting skill. VoxConverse (TV debates and news, K from 1 to 21) is where
counting ability is actually measured.

The old project's errors were grouped into **failure modes**, and the v2 design targets each one:

| ID | Failure | Example | Planned countermeasure |
|---|---|---|---|
| A | A tiny extra cluster (0–2 % of segments) from overlap, laughter or noise | ES2004a/b, TS3003b/c | overlap-aware training labels; *pruning* tiny clusters |
| B | One speaker split into two (drift across a 40-minute meeting) | EN2002a/d | *AffinityNet* with session context and time encoding; *merging* near-duplicate clusters |
| C | One dominant cluster swallows others (90/6/2/2 sizes) | TS3003a | report DER and cluster health, not only K |
| D | No clear eigengap, so K̂ hits the maximum | old SpectralNet | full-batch SpectralNet v2 on the right affinity, checked against exact eigenvalues |
| E | Too slow (about 800 dense eigendecompositions per meeting) | 25.7 min | cap on p, coarse-to-fine search, sparse eigensolver |
| F | "Silent" experiments that changed nothing without anyone noticing | two identical "different" runs | save the resolved config per run; warn when two methods give identical K̂ |

The old **Siamese network** also had concrete code flaws:
- a ReLU on its output, so all cosines were ≥ 0;
- training on Euclidean distance but inference on cosine;
- squeezing 192-d ECAPA into 64-d;
- only 4 random pairs per anchor, labelled from the most-overlapping speaker;
- no session context;
- no validation.

---

## 4. Research questions and hypotheses

1. **RQ1 – learned affinity.** Can a *session-level* model (one that looks at a whole meeting at once) refine ECAPA
   embeddings so that the similarity graph has a cleaner eigengap? Hypothesis: yes, especially for failure B (drift).
2. **RQ2 – SpectralNet done right.** If SpectralNet is trained full-batch on the *same* sparse affinity NME-SC uses, does it
   reproduce the exact eigengap count, and what does a parametric map add (speed, out-of-sample labelling)?
3. **RQ3 – post-processing.** How much do simple, validation-tuned rules (prune tiny clusters, merge near-duplicates)
   help, and what do they break?
4. **RQ4 – dependence on K and domain.** How does error grow with the true number of speakers, and do models and
   thresholds learned on meetings (AMI) transfer to broadcast speech (VoxConverse)?
5. **RQ5 – realism.** Do the gains survive a real VAD instead of the oracle one?

---

## 5. The v2 system

```
audio → VAD (oracle | pyannote) → 1.5 s / 0.75 s windows → ECAPA 192-d (cached)
      → [AffinityNet: refine embeddings using the whole session]          (optional)
      → cosine affinity → fast NME-SC: choose p*, sparse graph W
      → eigenvalues of L(W):  exact eigh   OR   SpectralNet v2 (Ritz values)
      → eigengap → K̂ → k-means labels
      → post-processing: prune clusters < share s, merge centroids with cosine > m
      → final K̂, labels → metrics, DER, plots
```

### 5.1 Data and labels
- **Segments:** windows as described above. Intervals shorter than 1.5 s are dropped, and a single window is centred.
  The segment counts match the old project exactly (for example EN2002a 2243, IS1009a 700).
- **Overlap-aware labels** (used only for training and analysis, never at inference):
  - A window is *clean* if one speaker covers ≥ 90 % of it and every other speaker ≤ 10 %.
  - Otherwise it is *ambiguous*.
  - On AMI, about 29 % of windows are ambiguous (meetings have a lot of overlap). On VoxConverse it is about 1–3 %.
  - Ambiguous windows are still fed to AffinityNet as context but are excluded from the loss. This fixes the old
    "label = speaker with most overlap" noise.

### 5.2 AffinityNet (replaces the Siamese network)
- **Input:** all ECAPA vectors of a session (or a chunk of 256–1024 consecutive segments) plus each segment's centre time.
- **Architecture:**
  - Linear 192→256, plus a sinusoidal **time encoding** (periods 1 s to 4000 s), so the model knows *when* each segment
    occurred.
  - Then a 4-layer pre-LayerNorm **Transformer** (256-d, 4 heads), so every segment can see every other segment in the
    session.
  - Then a linear head back to 192-d with **no activation**.
- **Residual over ECAPA:** z = normalize(x + α·head(h)), with α learnable and initialised at 0.1, and a very small head
  initialisation. At the start the model *is* raw ECAPA, so in principle it cannot start worse than the baseline.
- **Loss** (clean segments only):
  - BCE on **all pairs** in the chunk, on a scaled cosine with class-balancing weights. Using all pairs gives hard
    negatives automatically, and the model trains on the same metric it is evaluated on (cosine).
  - Plus 0.5 × supervised contrastive loss (temperature 0.1).
- **Augmentation:**
  - *Speaker dropout* (p = 0.5): delete all segments of random speakers, so the model sees K = 1–4, not always 4.
  - Embedding noise.
  - 10 % segment dropout.
- **Optimisation:** AdamW 3e-4, warm-up plus cosine decay, gradient clipping, at most 60 epochs, early stopping (patience 8).
- **Model selection:** every epoch, the full counting pipeline runs on the validation set, and the checkpoint with the
  best `val_score` (count MAE / relative error on validation) is kept.

### 5.3 Fast NME-SC
- The neighbour count p is capped at min(0.25·N, 60).
- **Coarse-to-fine search:** p on a stride-4 grid, then every p within ±4 of the best coarse value.
- Only the smallest k_max+1 eigenvalues are computed, with a sparse solver (`eigsh`). Connected components are handled
  explicitly: a disconnected graph has repeated zero eigenvalues, which made the sparse solver unreliable, so that case is
  solved directly with a fallback to dense. Sparse and dense agree on 16/16 test recordings.
- The final decomposition at p\* is dense and exact.
- Laplacian: unnormalized (best in the old project); sym_norm is an ablation.

### 5.4 SpectralNet v2
This is SpectralNet with each cause of the old failure removed:
1. It trains on **NME-SC's sparse affinity at p\***, not a fixed Gaussian kNN graph.
2. **Full batch:** all segments of a session in every step, so the orthogonalisation is exact rather than a noisy
   minibatch estimate.
3. The network is an MLP 192→256→256→(k_max+1) with a linear output, then a **Cholesky orthonormalisation layer**, so the
   outputs Y satisfy YᵀY = N·I.
4. **Loss** trace(YᵀLY)/N, the Laplacian energy. Its minimum is reached by the bottom eigenvectors.
5. **Rayleigh–Ritz:** eigenvalues of the small matrix YᵀLY/N approximate the bottom eigenvalues of L, and K̂ is read
   from their eigengap.
6. **Self-check:** for every recording the Ritz values and K̂ are compared with exact `eigh`, and the agreement rate is
   reported.
7. **Warm start** (optional): start each session's network from one pre-trained on training sessions.
8. **Out-of-sample test:** train on 90 % of a recording's segments and label the held-out 10 % with the trained map.

### 5.5 Post-processing
- **Prune:** clusters with a share below `min_cluster_share` are dissolved, and their segments go to the nearest centroid.
- **Merge:** while two centroids have cosine above `merge_threshold`, merge them.
- **Single-speaker check:** if the mean cosine is very high, set K̂ = 1.
- The thresholds were grid-searched on **validation data only** (separately per method). In this project that was AMI
  dev only, because VoxConverse dev is not available.

### 5.6 Methods compared

| id | affinity | count backend | post-processing |
|---|---|---|---|
| `baseline_mode` | – | always the most common K of the training split (4 for AMI) | – |
| `nmesc_ecapa` | raw ECAPA | exact eigh | none (reproduces the old best) |
| `nmesc_ecapa_pp` | raw ECAPA | exact eigh | tuned |
| `nmesc_affnet`, `nmesc_affnet_pp` | AffinityNet | exact eigh | none / tuned |
| `snet_affnet_pp` | AffinityNet | SpectralNet v2 | tuned (**main proposed system**) |
| `snet_ecapa_pp` | raw ECAPA | SpectralNet v2 | tuned (isolates SpectralNet's contribution) |

### 5.7 Evaluation protocol
- **Splits:**
  - AMI train (136 meetings) is for training, AMI dev (18) for validation and all tuning, AMI test (16) for final
    numbers only.
  - VoxConverse test has 232 recordings. VoxConverse dev was meant to be split 80/20 into train/validation, but it is
    not available (see §8).
- **Metrics:**
  - exact, ±1, MAE, signed error, relative accuracy;
  - DER (pyannote.metrics, 0.25 s forgiveness collar on each side);
  - per-K-bin errors;
  - cluster health (largest and smallest cluster share, gap ratio, saturation at k_max).
- **Statistics:** paired bootstrap (10 000 resamples) 95 % confidence intervals for the difference from `nmesc_ecapa`, and
  a Wilcoxon signed-rank test on |K̂ − K|.
- **Rules followed:**
  - Nothing is tuned or selected on test data. If a variant does better on test but worse on validation, it is
    reported but not adopted.
  - Every run saves its resolved config and git commit.

---

## 6. What was done: phase by phase

| Phase | Work | Outcome |
|---|---|---|
| 0 Setup | Package skeleton, layered YAML config with `--set` overrides (unknown keys raise errors), `check-data`, `make-splits` | Data check: AMI complete; VoxConverse test present (232 recordings, 43.5 h); **VoxConverse dev missing** |
| 1 Data pipeline | RTTM reader, oracle/pyannote VAD, segmentation, cached ECAPA, overlap labels, `prepare` | Segment counts identical to the old project; about 29 % ambiguous windows on AMI |
| 2 Baseline reproduction | Fast NME-SC, exact backend, mode baseline, evaluation, DER, reports | `nmesc_ecapa` reproduces the old 9/16 exact **exactly**, and clustering time drops from 25.7 min to **1.1 min** |
| 3 Post-processing | Prune / merge / single-speaker rules and a validation-only grid search | AMI dev exact 0.67 → 0.94 for raw ECAPA |
| 4 AffinityNet | Model, loss, sampler, training with early stopping, chunked inference (unit-tested equal to full inference) | AMI dev 18/18 exact (raw ECAPA 12/18) |
| 5 SpectralNet v2 | Full-batch net, Cholesky orthonormalisation, Ritz values, self-check, warm start, out-of-sample test | 100 % K̂ agreement with exact eigh; out-of-sample label agreement 0.90 |
| 6 Final evaluation | AMI test for all methods, 10 ablation families, pyannote VAD | §7.1–7.3 |
| 7 WavLM embedder | Optional; **skipped** by decision (it would need a new package) | – |
| 8 Reports | `compare` produces SUMMARY.md, `plots` produces 54 figures, hand-written inferences | `results/SUMMARY.md` |
| Extra | **Cross-corpus test:** AMI-trained models and thresholds applied unchanged to VoxConverse test | §7.4 |

Engineering issues met along the way:
- **Shared GPU.** Another job used about 22 GB of the 24 GB GPU, so every GPU step got a CPU fallback on out-of-memory.
- **Machine reboot.** One reboot killed an overnight run, so the batch scripts gained a resume option (`START_AT=N`).
- **Sparse eigensolver.** It failed on disconnected graphs; this was fixed with explicit connected-component handling.

---

## 7. Results

### 7.1 AMI test (16 meetings, oracle VAD)

| method | exact | MAE | DER |
|---|---|---|---|
| baseline_mode ("always 4") | **0.938** | **0.062** | – |
| nmesc_ecapa (old best) | 0.562 | 0.438 | 0.127 |
| nmesc_ecapa_pp | 0.750 | 0.250 | 0.126 |
| nmesc_affnet / _pp | 0.812 | 0.500 | 0.150 |
| snet_affnet_pp (main proposed system) | 0.812 | 0.500 | 0.160 |
| **snet_ecapa_pp** | **0.875** | **0.125** | 0.128 |

- `snet_ecapa_pp` is the only method that is **statistically better** than `nmesc_ecapa`: Δ MAE −0.31, 95 % CI
  [−0.56, −0.12], p = 0.025.
- No method beats "always 4". On AMI that is expected, and it is why VoxConverse matters.
- **AffinityNet:**
  - It fixed the drift/split cases it was designed for: EN2002a/d go from K̂ = 5 to 4 with balanced clusters, and
    ES2004a/b and TS3003b/c are also fixed.
  - It created two large overcounts: IS1009a K̂ = 7 and TS3003d K̂ = 8.
  - The cause is that it raised *all* cosines (mean 0.16 → 0.45), which splits speaker blocks into sub-blocks. In both
    cases the true K was the second-best eigengap.
- **Model selection was the weak point.**
  - AMI dev has only 18 meetings, all with K = 4.
  - The chosen epoch was a one-epoch spike in the validation score, while the pair EER (the smoother metric) was getting
    worse, which is a sign of overfitting.
  - Every ablation variant ranked worse than the default on dev but better or equal on test. This is the signature of
    noisy selection.
- Pyannote VAD on AMI test:
  - Counting got slightly *better* for raw ECAPA: 0.688 vs 0.562 exact. Pyannote drops short and overlapped bits that
    otherwise seed spurious clusters.
  - DER rose (0.127 → 0.169), as expected with real VAD errors.

### 7.2 SpectralNet v2 (RQ2)
- K̂ agreement with exact eigh is **100 %** (18/18 dev, 16/16 test), with no saturations. The old SpectralNet had 0.125
  exact accuracy and hit k_max.
- Ritz eigenvalue error: median 9–11 % of λ_(k_max+1); the errors are on near-zero eigenvalues and do not move the gap.
- Out-of-sample labelling: 0.90 mean agreement. The target was 0.95; it is missed because one recording flipped K.
- No speed gain (3.9 min vs 1.1 min on AMI test), partly because of the exact self-check. The warm start had no effect.
- `snet_ecapa_pp` beat `nmesc_ecapa_pp` on two recordings. This is because its k-means space gives slightly different
  cluster sizes, so pruning acts differently. It is *not* because SpectralNet counts differently.

### 7.3 Ablations (AMI; full table in SUMMARY §3)

| Change | Effect |
|---|---|
| sym_norm Laplacian instead of unnormalized | slightly worse (as in the old project) |
| Remove the Transformer (0 layers) | dev slightly worse, test MAE better |
| Remove the time encoding | dev worse (0.89), test 16/16. **Not adopted**: validation said otherwise |
| BCE only / old "most-overlap" labels / no speaker dropout | worse on dev, mixed on test (selection noise) |
| Oracle overlap removal (upper bound, uses the reference) | raw ECAPA 0.56 → 0.75. Overlap is a real but partial cause of +1 errors |
| Wang et al. refinement ops | help raw ECAPA (0.56 → 0.81) but wreck AffinityNet (0.69, DER 0.23) |
| Old Siamese with only flaws 1–2 fixed | collapses (0/16). Fixing the two bugs is not enough |

### 7.4 VoxConverse test, cross-corpus (232 recordings, K = 1–21; everything trained and tuned on AMI)

| method | exact | ±1 | MAE | DER |
|---|---|---|---|---|
| always 4 | 0.095 | 0.228 | 3.56 | – |
| **nmesc_ecapa** | **0.409** | **0.595** | 2.35 | 0.125 |
| nmesc_ecapa_pp | 0.358 | 0.539 | **2.09** | **0.079** |
| snet_ecapa_pp | 0.302 | 0.496 | 2.54 | 0.090 |
| nmesc_affnet(_pp), snet_affnet_pp | 0.293 | 0.573 | 2.75–2.78 | 0.18 |
| pyannote VAD: nmesc_ecapa / snet_affnet_pp | 0.405 / 0.293 | 0.591 / 0.530 | 2.41 / 2.93 | 0.155 / 0.212 |

- **The AMI ranking reverses.** Plain raw-ECAPA NME-SC has the best exact accuracy.
  - The AffinityNet systems are *significantly worse*: Δ MAE +0.39 [+0.13, +0.69], p = 0.003. They add about one
    speaker at every K ≤ 7, which is the same "inflated cosine" symptom seen on AMI.
  - Post-processing has the lowest MAE and DER but loses exact accuracy.
- **Two error regimes, found from the per-recording diagnostics:**
  - *Short recordings are massively overcounted.* On the 12 shortest recordings (under about 90 segments), NME-SC picks
    p\* = 1–2. The nearest-neighbour graph falls apart and K̂ becomes 14–24. MAE is 17.6 on those 12 and 1.5 on the other
    220. This is a flaw in the p-selection rule for small N, not in the embeddings.
  - *Many-speaker recordings are undercounted.* For K ≥ 13 the signed error is −3.4 to −8.5. A 2–3 % pruning threshold
    tuned on 4-person meetings deletes real minor speakers in TV debates.
- Unlike on AMI, all methods are far above the "always 4" baseline, so on VoxConverse genuine counting is visible.

### 7.5 Success criteria from the plan

| Target | Result | Met? |
|---|---|---|
| AMI exact ≥ 0.80 for snet_affnet_pp | 0.8125 | yes (but below always-4) |
| AMI MAE ≤ 0.25 | 0.50 | no |
| VoxConverse MAE −20 % vs nmesc_ecapa | +18 % (cross-corpus) | no; the VoxConverse-trained run is pending |
| SpectralNet/exact agreement ≥ 90 % | 100 % | yes |
| No K̂ = k_max saturation on AMI | 0 | yes |
| AMI clustering ≤ 3 min | 1.1 min exact; 3.9 min SpectralNet | exact yes, SpectralNet no |

---

## 8. Research perspective: what this project shows

1. **The evaluation set decides what you can conclude.** On AMI a constant answer wins, so a method's AMI score mostly
   measures bias towards 4. Any counting claim needs a corpus with a wide K range. This project shows it concretely:
   the AMI winner (`snet_ecapa_pp`) is mid-table on VoxConverse.
2. **Validation design is the bottleneck for learned affinities.** AffinityNet *can* fix speaker drift (failure B), but
   selecting it on 18 all-K=4 meetings picked a noisy epoch that inflated similarities. The model did not fail as an
   idea; selection did. Speaker-dropout validation variants, a smoother selection metric, or VoxConverse validation data
   are the fix.
3. **A learned metric needs calibration.** NME-SC binarises by rank, but the eigengap still depends on how
   block-diagonal the affinity is. A model that raises all cosines (mean 0.16 → 0.45) blurs block boundaries. A
   calibration or regularisation term on cross-speaker cosines is a principled next step.
4. **SpectralNet is fixable, but it is not a speed win here.** Full-batch training on the right graph makes SpectralNet
   agree exactly with eigh. That answers *why* the old one failed (minibatch orthogonalisation plus the wrong affinity).
   At N ≤ 6 000, exact eigh is cheap, so SpectralNet's value is the parametric map, not speed.
5. **Simple post-processing is powerful but corpus-specific.** Pruning gave the largest single AMI gain. With an AMI-tuned
   threshold it removes real speakers on VoxConverse. Thresholds should depend on K or duration, or be tuned per domain.
6. **The p-selection rule of NME-SC has a small-N failure** (p\* = 1–2 shatters the graph). This is not discussed in the
   original method, and short recordings are common in practice.

**Threats to validity:**
- AMI test has n = 16, so the confidence intervals are wide.
- VoxConverse results are cross-corpus only; nothing was tuned on VoxConverse.
- Oracle VAD is optimistic.
- Phase 7 (WavLM) was not run.
- All numbers use one seed.

---

## 9. Next steps (ranked)

1. **Obtain VoxConverse dev**, then:
   - make the stratified 80/20 split;
   - retrain AffinityNet on AMI + VoxConverse into a *new* checkpoint folder (keep the AMI-only model);
   - retune on AMI dev + VoxConverse validation;
   - re-evaluate both test sets and compare with the tagged AMI-only and cross-corpus results.
2. Add a **minimum p** (or a component-share cap on K̂) for short recordings, tuned on validation.
3. Make the **prune threshold depend on K or duration**, tuned on validation.
4. **Robust AffinityNet selection:** pair EER plus count error on speaker-dropout validation variants; EMA or averaged weights.
5. **Cosine calibration term** for AffinityNet.
6. Use the gap ratio: prefer the runner-up K when the top gap is not clearly dominant.
7. Speed up SpectralNet (sample the self-check, cap the steps).
8. Optional: a WavLM embedder.

---

## 10. Reproducing everything

```bash
PY=/home/pm_students/miniconda3/envs/spectral/bin/python
$PY run.py check-data                       # data summary
bash scripts/run_all.sh                     # AMI pipeline end to end (~1.5 h)
bash scripts/overnight.sh                   # SpectralNet, final eval, ablations (START_AT=N resumes)
bash scripts/vox_crosscorpus.sh             # VoxConverse cross-corpus test (~70 min)
$PY run.py compare && $PY run.py plots      # SUMMARY.md and figures
python tests/run_tests.py                   # 20 unit/integration tests
```

Results layout: `results/<corpus>/<split>/<method>[/<tag>]/`. Each run folder contains:
- `predictions.csv` (one row per recording with all diagnostics);
- `summary.md`;
- `config_resolved.yaml` and `git_commit.txt`;
- per-recording `.npz` files (eigenvalues, labels, embeddings).

Cross-corpus runs carry the tag `ami_trained`.

### Key figures to show when presenting
- `metrics_bar_ami.png`: methods vs "always 4", with confidence intervals.
- `error_vs_k_vox_amitrained.png`: error against true K on VoxConverse (the two regimes).
- `scatter_k_voxconverse_amitrained.png`: K̂ vs K; the short-recording overcounts are visible top-left.
- `spectrum_IS1009a.png` and `affinity_IS1009a.png`: why AffinityNet overcounts (second-best eigengap = truth).
- `affinity_EN2002a.png`: AffinityNet fixing a split speaker.
- `cluster_shares_ami.png`: what pruning can and cannot fix.
- `train_curves.png`: the noisy model-selection epoch.
- `timing.png`: speed of each backend.

---

## 11. Likely questions and short answers

- **Why not just predict 4 on AMI?** On AMI that wins, which is exactly why AMI cannot measure counting. On VoxConverse
  it scores 9.5 % exact against 41 % for real clustering.
- **Did AffinityNet work?** Partly. It fixed the drift cases it was designed for, but its chosen checkpoint inflated
  similarities and overcounts. That is mainly a validation-data problem, and it does not transfer to VoxConverse yet.
- **Why keep the no-time-encoding variant out when it scored 16/16 on test?** Choosing a model by its test score is
  tuning on test. Validation preferred the default, so the default is reported.
- **What is the main contribution?**
  - A reproducible, 23× faster version of the baseline.
  - A corrected SpectralNet that matches exact spectral counting.
  - A session-level learned affinity with a clear analysis of when it helps and why it fails.
  - Evidence on how counting error depends on K and domain, including a previously unreported small-N failure of NME-SC.
