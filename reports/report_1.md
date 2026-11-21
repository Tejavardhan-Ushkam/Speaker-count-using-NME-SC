# Report 1: speaker counting with snet_ecapa_pp, results up to 2026-11-21

Code state: git tag `vox-snet-warm-v1` plus commit 620b263. All numbers below are recomputed from the saved `predictions.csv` files; nothing was tuned on test data.

## 1. What was tested

| Method | What it is |
|---|---|
| baseline_mode | Always predicts the most common speaker count of the training corpus (AMI: 4, VoxConverse: 2) |
| nmesc_ecapa | Standard NME-SC spectral clustering on ECAPA embeddings, eigengap → K̂ (reference method) |
| snet_ecapa_pp | ECAPA → NME-SC graph → SpectralNet eigenvectors → post-processing (pruning of small clusters, centroid merge) |

There are two versions of snet_ecapa_pp:

* **AMI-only:** p_min = 1, post-processing tuned on AMI dev.
* **VoxConverse-tuned:** tuned on AMI dev + VoxConverse val. The tuning chose p_min = 4 (a floor on the number of graph neighbours), relative pruning 0.15/K̂ and merge 0.7. Pre-training SpectralNet on VoxConverse train changed nothing (MAE 1.875 → 1.862, p = 0.33), so it is not used.

## 2. Headline results

**VoxConverse test (232 recordings, 1–21 speakers)**

| Method | Exact | ±1 | MAE | DER |
|---|---|---|---|---|
| Always 2 | 0.134 | 0.276 | 4.61 | – |
| nmesc_ecapa | 0.409 | 0.595 | 2.35 | 0.125 |
| snet_ecapa_pp, AMI-only | 0.302 | 0.496 | 2.54 | 0.090 |
| snet_ecapa_pp, VoxConverse-tuned | 0.379 | 0.608 | 1.875 | 0.077 |
| same, without pruning/merge (analysis only) | 0.444 | 0.630 | 1.48 | – |

**AMI test (16 meetings: 15 with 4 speakers, 1 with 3)**

| Method | Exact | ±1 | MAE | DER |
|---|---|---|---|---|
| Always 4 | **0.938** | 1.000 | **0.062** | – |
| nmesc_ecapa | 0.562 | 1.000 | 0.438 | 0.127 |
| snet_ecapa_pp, AMI-only | 0.875 | 1.000 | 0.125 | 0.128 |
| snet_ecapa_pp, VoxConverse-tuned | 0.875 | 1.000 | 0.125 | 0.129 |
| same, without pruning/merge (analysis only) | 0.500 | 1.000 | 0.500 | 0.129 |

On AMI the trivial "always 4" baseline is best, because the test set has almost no variation in speaker count. AMI test is therefore not informative about counting ability; it only shows that a method does not over-count meetings.

## 3. Operating range on VoxConverse test (cumulative speaker-count ranges)

The ranges overlap; recordings with exactly 10 speakers count in both "1–10" and "10+".

**snet_ecapa_pp, VoxConverse-tuned (with pruning)**

| True K | 1 | 1–2 | 1–4 | 1–6 | 4–6 | 4–8 | 1–10 | 10+ | All |
|---|---|---|---|---|---|---|---|---|---|
| Recordings | 15 | 46 | 86 | 117 | 53 | 107 | 196 | 46 | 232 |
| Exact | 0.87 | 0.89 | 0.66 | 0.59 | 0.38 | 0.31 | 0.44 | 0.09 | 0.38 |
| Within ±1 | 1.00 | 1.00 | 0.91 | 0.84 | 0.72 | 0.61 | 0.68 | 0.24 | 0.61 |
| MAE | 0.13 | 0.11 | 0.44 | 0.65 | 1.08 | 1.59 | 1.37 | 4.20 | 1.88 |
| Signed error | +0.13 | +0.02 | −0.30 | −0.51 | −0.92 | −1.50 | −1.28 | −4.15 | −1.79 |

**Same model without pruning/merge (analysis only)**

| True K | 1 | 1–2 | 1–4 | 1–6 | 4–6 | 4–8 | 1–10 | 10+ | All |
|---|---|---|---|---|---|---|---|---|---|
| Exact | 0.80 | 0.87 | 0.70 | 0.66 | 0.55 | 0.45 | 0.52 | 0.11 | 0.44 |
| Within ±1 | 0.87 | 0.93 | 0.90 | 0.86 | 0.81 | 0.66 | 0.70 | 0.30 | 0.63 |
| MAE | 0.33 | 0.20 | 0.41 | 0.50 | 0.68 | 1.17 | 1.08 | 3.41 | 1.48 |
| Signed error | +0.33 | +0.15 | −0.08 | −0.21 | −0.45 | −0.81 | −0.70 | −3.15 | −1.15 |

**nmesc_ecapa (reference)**

| True K | 1 | 1–2 | 1–4 | 1–6 | 4–6 | 4–8 | 1–10 | 10+ | All |
|---|---|---|---|---|---|---|---|---|---|
| Exact | 0.53 | 0.74 | 0.64 | 0.60 | 0.51 | 0.42 | 0.47 | 0.09 | 0.41 |
| Within ±1 | 0.60 | 0.80 | 0.79 | 0.77 | 0.75 | 0.63 | 0.64 | 0.37 | 0.59 |
| MAE | 4.80 | 2.46 | 2.45 | 2.26 | 1.60 | 1.65 | 2.15 | 3.26 | 2.35 |

## 4. Findings

1. **The mean MAE gain over NME-SC comes from 13 short recordings.** On the 13 recordings with at most 90 segments, NME-SC predicts 14–24 speakers (MAE 16.3), while the tuned model is near-correct (MAE 0.62). On the other 219 recordings the tuned model is worse: MAE 1.53 → 1.95, Wilcoxon p = 4e-8. Recording by recording, it is better on 30, worse on 75 and equal on 127.
2. **The useful setting on VoxConverse is p_min = 4.** It stops the graph of short recordings from splitting into many tiny components.
3. **Pruning helps AMI and hurts VoxConverse.**
   * On AMI it removes small junk clusters: exact 0.50 → 0.875.
   * On VoxConverse it removes real speakers who talk little: exact 0.444 → 0.379, with 5 recordings fixed and 20 broken.
   * The tuning used one shared setting and averaged the two corpora's scores, so AMI decided it.
   * Validation already showed the harm: at p_min = 4, VoxConverse val exact stays at 0.605 with or without pruning, and MAE rises from 0.72 to 0.81.
4. **Errors are one-sided under-counts.** With pruning, 135 recordings are under-counted and 9 over-counted (signed error −1.79). The under-count grows with K.
5. **Above 10 speakers every method fails** (9–11 % exact). The ECAPA embeddings of speakers who talk only briefly do not form separate clusters, and no graph or pruning setting can create those clusters.
6. **DER 0.077 vs 0.125** is a mean driven by the short files. It is not significant recording by recording (Wilcoxon p = 0.48).

## 5. Where the model stands for 1–6 speakers

| VoxConverse test, true K 1–6 (117 recordings) | Exact | ±1 | MAE |
|---|---|---|---|
| nmesc_ecapa | 0.60 | 0.77 | 2.26 |
| snet_ecapa_pp, VoxConverse-tuned | 0.59 | 0.84 | 0.65 |
| same, without pruning/merge | 0.66 | 0.86 | 0.50 |

* **Within ±1 and MAE:** the model is clearly better than NME-SC.
* **Exact accuracy:** the selected (pruned) model is not better than NME-SC. Only the unpruned variant is, and it was not selected on validation.

## 6. Decision

* **Scope:** the next phase is limited to recordings with 1–6 speakers.
* **Target:** at least 65 % exact on every test corpus.
* **Method:** all choices are made on validation and training data only; each test set is run once at the end. See report 2.
