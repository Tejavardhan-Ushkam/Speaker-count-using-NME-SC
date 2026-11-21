## 4. Success criteria (prompt §10) — AMI only

| Metric | Old best | Target for `snet_affnet_pp` | Result | Met? |
|---|---|---|---|---|
| AMI test exact | 0.5625 | ≥ 0.80, and compared against "always 4" (0.9375) | **0.8125**; always-4 = 0.9375 | ≥ 0.80 yes; **below the always-4 baseline** |
| AMI test MAE | 0.4375 | ≤ 0.25 | **0.500** | **no** — two large overcounts (IS1009a K̂=7, TS3003d K̂=8) |
| VoxConverse MAE / rel. acc | – | ≥ 20 % MAE reduction vs `nmesc_ecapa` | cross-corpus only (AMI-trained): `nmesc_ecapa` 2.35; best `nmesc_ecapa_pp` 2.09 (−11 %, n.s.); `snet_affnet_pp` 2.78 (+18 %) | **no** (as measured cross-corpus; Vox-trained run pending VoxConverse dev) |
| SpectralNet vs exact K̂ agreement | – | ≥ 90 % | **100 %** (18/18 dev, 16/16 test) | yes |
| K̂ = k_max saturations | 2/16 | 0 | **0** | yes |
| AMI test clustering time | 25.7 min | ≤ 3 min | 1.1 min (exact backend); **3.9 min** (`snet_affnet_pp`) | exact yes; SpectralNet **no** (the per-recording exact eigh self-check is ~1 min of it) |

The best AMI test system is **`snet_ecapa_pp`** (raw ECAPA → NME-SC p* → SpectralNet v2 → pruning 3 % + merge 0.6):
exact 0.875, MAE 0.125, DER 0.128, and the only method whose improvement over `nmesc_ecapa` has a bootstrap CI
excluding 0 (Δ MAE −0.31 [−0.56, −0.12], Wilcoxon p = 0.025). It is still not better than always answering 4.

## 5. Inferences

**Did AffinityNet beat raw ECAPA?** On validation, yes (AMI dev 18/18 vs 12/18). On AMI test, only partly:
exact 0.81 vs 0.56, but MAE 0.50 vs 0.44 and DER 0.150 vs 0.127 — not significant (Δ MAE +0.06 [−0.50, +0.75], p = 0.85).
- *Fixed failure B (speaker split in two):* EN2002a and EN2002d go from K̂=5 (5th cluster 5–6 %) to 4 with balanced
  sizes (37/23/23/17, 32/31/22/15); ES2004a/b and TS3003b/c are also fixed. These were exactly the drift/split cases
  the session context was meant to fix.
- *Created new large errors:* IS1009a (K̂=7, sizes 37/25/17/9/5/4/2) and TS3003d (K̂=8). In both, the second-best
  eigengap is the true K=4 (gap ratio 1.37 and 1.41) — `spectrum_IS1009a.png` shows the gap at 4 (0.77) losing to the
  gap at 7 (1.05). `affinity_IS1009a.png` shows why: AffinityNet raises every cosine (mean cosine 0.16 → 0.45 on test)
  and splits a speaker block into sub-blocks. `tsne_EN2002a.png` shows a second symptom: one speaker (MEE071) is
  pulled into the ambiguous/overlap cloud.
- *Failure C (dominant cluster) is not fixed:* TS3003a is 92/6/2 → K̂=3 (raw ECAPA got 4 but with sizes 90/6/2/2).
- **Why:** the checkpoint was selected by `val_score` on AMI dev, which is all K=4 and only 18 recordings.
  `train_curves.png` shows the chosen epoch 19 is a one-epoch spike (MAE 0) between epochs at 0.22–0.45, while pair EER
  rises from 0.079 (epoch 9, better than raw ECAPA's 0.094) to 0.113 — the model was overfitting and the pick was luck.
  Every ablation variant (no time encoding, BCE only, most-overlap labels, 0 layers) scores *worse* than the default on
  dev but *better or equal* on test, the signature of selection noise rather than real differences. The no-time-encoding
  model gets 16/16 on test; per rule §0.6 it is **not** adopted, because dev said otherwise.

**Did SpectralNet v2 match the exact backend, and did it add anything?** It matches: K̂ agreement 100 % on dev and
test (old SpectralNet: 0.125 exact, K̂ up to k_max), no saturations, Ritz values within a median 9–11 % (max 22 %) of the
exact eigenvalues relative to λ_(k_max+1) (`spectrum_*.png`; the larger *relative* errors are on near-zero within-cluster
eigenvalues and do not move the eigengap). What it adds: (1) a parametric map — on held-out 10 % of 3 AMI dev
recordings label agreement was 0.99 on two and 0.72 on ES2011a, mean **0.90 (target 0.95, missed)** because the 90 %
subset of ES2011a flipped K from 4 to 5; (2) slightly different labels from its k-means space, which is why
`snet_ecapa_pp` (0.875) beats `nmesc_ecapa_pp` (0.75) on test on two recordings: TS3003a (SpectralNet's clusters
84/7/6/4 survive pruning, while NME-SC's 90/6/2/2 loses one → K̂=3) and TS3003d (the tuned 3 % prune share, vs 2 %,
removes its 2 % cluster). It adds **no speed**: ~10 s fit per recording plus the exact self-check (3.9 min vs
1.1 min). The warm start does not help on AMI (14.4 vs 14.8 s/recording, identical K̂): 500-step fits converge either way.

**How much did post-processing help, and where did it hurt?** On raw ECAPA it is the single most effective change:
AMI dev exact 0.67 → 0.94, test 0.56 → 0.75 (NME-SC) / 0.875 (SpectralNet). It removes the tiny 5th clusters of ES2004a/b
and TS3003b/c (0–2 %, failure A). It cannot fix EN2002a/d, whose extra cluster is 5–6 % (failure B), above the threshold
(`cluster_shares_ami.png`: wrong counts above the black line survive). It hurt TS3003a: the 2 % and 2 % clusters were real
speakers squeezed by the dominant one (90 %), so pruning went 4 → 3 (failure C, the predicted trade-off). On AffinityNet
the tuner picked *no* post-processing, because the dev set had nothing left to fix; this is why `nmesc_affnet_pp` and
`snet_affnet_pp` give the same K̂ as `nmesc_affnet` (the no-op warnings above are expected, not bugs) — and why nothing
caught the IS1009a/TS3003d overcounts on test.

**How does the error depend on true K (VoxConverse, cross-corpus — §1b)?** All models and thresholds were trained and
tuned on AMI only and applied unchanged to VoxConverse test (232 recordings, K = 1–21); nothing was fitted on VoxConverse.
- *AMI's ranking does not transfer.* The best Vox method on exact accuracy is plain `nmesc_ecapa` (0.409, MAE 2.35).
  Post-processing gives the lowest MAE (`nmesc_ecapa_pp` 2.09, not significant: Δ MAE −0.27 [−0.77, +0.19]) and the lowest
  DER (0.079), but loses exact accuracy (0.358). Every AffinityNet system is significantly *worse* than raw ECAPA (exact
  0.293, Δ MAE +0.39 [+0.13, +0.69], p = 0.003). AMI's best method, `snet_ecapa_pp`, falls to 0.302. "Always 4" scores 0.095,
  so on Vox the counting methods clearly beat the prior, which AMI could not show.
- *Error depends on K in two opposite regimes* (`error_vs_k_vox_amitrained.png`):
  - Small K (1–3) is overcounted by the methods without post-processing (K=1: MAE 4.8 raw, 5.3 AffinityNet). The cause is
    one specific failure. In 12 short recordings (≤ 88 segments, < 3 min), NME-SC picks p* = 1–2. The 1-NN graph then
    breaks into many components, and the eigengap returns K̂ = 14–24 (MAE 17.6 on those 12; 1.52 on the other 220, exact
    0.43). Post-processing hides this by pruning the fragments (K=1 MAE 0.8), so the error is in the p* search, not in
    the embeddings.
  - Large K (8+) is undercounted by every method (signed error −1.7 to −8.5 for K 13+). Pruning with AMI's 2–3 % share
    removes real minor speakers: `nmesc_ecapa_pp` undercounts by more than 5 on 21 recordings, and K 13+ MAE goes from 3.9
    (raw) to 6.8 (pp) and 8.5 (`snet_ecapa_pp`). A share tuned on 4-speaker meetings is too high for TV debates with many
    short-turn speakers.
- *AffinityNet does not generalise across corpora.* It was selected on 18 AMI dev meetings, all with K = 4 (see the
  selection-noise discussion above). On Vox it adds about +1 speaker at every K ≤ 7 (signed +1.3 to +5.3), which is the
  same "raised cosines split a speaker" symptom as IS1009a/TS3003d, and it saturates at k_max = 25 three times.
- *SpectralNet* gives the same K̂ as the exact backend on Vox too (`snet_affnet_pp` vs `nmesc_affnet_pp`: same exact /
  ±1, MAE 2.78 vs 2.75). The extra error comes from short recordings, where a 500-step fit on < 90 points is noisier.
- *Realistic VAD* (pyannote) barely changes counting on Vox (`nmesc_ecapa` 0.405 vs 0.409 oracle). DER rises
  0.125 → 0.155.
- These are cross-corpus numbers and are not the plan's Vox targets: the ≥ 20 % MAE reduction needs Vox-trained and
  Vox-tuned systems (Next steps 1).

**Pruning tuned on VoxConverse (tag `vox_tuned`).** VoxConverse dev was imported, verified, and split 173/43, stratified
by K. Two changes were added, both tuned on AMI dev + Vox val only:
- a relative pruning mode, which prunes clusters smaller than a fraction of the average cluster 1/K̂;
- a tuned NME-SC lower bound `p_min`.

Tuned values (`results/tuning_vox/`), with merge 0.7 in both:

| method | p_min | pruning |
|---|---|---|
| `nmesc_ecapa_pp` | 4 | absolute 3 % |
| `snet_ecapa_pp` | 4 | relative 0.15/K̂ |

| VoxConverse test | exact | ±1 | MAE | DER |
|---|---|---|---|---|
| always 2 (Vox-train mode) | 0.134 | 0.276 | 4.61 | – |
| `nmesc_ecapa` (no pp) | **0.409** | 0.595 | 2.35 | 0.125 |
| `snet_ecapa_pp`, AMI-tuned | 0.302 | 0.496 | 2.54 | 0.090 |
| **`snet_ecapa_pp`, Vox-tuned** | 0.379 | **0.608** | **1.88** | **0.077** |
| `nmesc_ecapa_pp`, Vox-tuned | 0.323 | 0.517 | 2.50 | 0.089 |

- **`snet_ecapa_pp` (Vox-tuned) has the lowest VoxConverse MAE.**
  - It is 20.3 % below `nmesc_ecapa` (Δ −0.48 [−1.03, +0.00], Wilcoxon p = 0.011). This meets the 20 % target in size,
    but the bootstrap CI only just touches 0.
  - It is clearly better than its own AMI-tuned version (Δ −0.67 [−0.91, −0.45]).
  - AMI test is unchanged: 0.875 exact, with the same two errors (EN2002a/d).
  - It still has lower *exact* accuracy than plain `nmesc_ecapa` on VoxConverse (0.379 vs 0.409).
- **`p_min` = 4 fixes the short-recording failure.** On the 13 shortest files MAE goes from 16.3 to 0.62, with K̂ ≤ 5;
  the earlier K̂ was 14–24. K=1 MAE goes from 4.8 to 0.13.
- **The relative threshold protects many-speaker recordings.** K 13+ MAE is 5.06 for SpectralNet with relative pruning,
  against 8.50 with absolute pruning.
- **`nmesc_ecapa_pp` got worse on VoxConverse** (MAE 2.09 → 2.50 against its AMI-tuned version). Its tuner chose
  absolute 3 %, which again deletes real minor speakers (K 13+ MAE 8.5). On AMI test it reached 0.812 exact but turned
  TS3003a into K̂=2.
  - This is a selection limitation: Vox val has only 43 recordings and 3 with K ≥ 11, so the absolute and relative rules
    score almost the same on validation.
  - Next fix: weight validation by K bin, or pool AMI dev + Vox val + speaker-dropout variants.

**SpectralNet warm start trained on VoxConverse (snet_ecapa_pp, tag vox_warm).** The only learned part of snet_ecapa_pp that had not yet seen VoxConverse is the SpectralNet starting network, so it was pre-trained on VoxConverse train (173 recordings, 50 steps each, 112 s on CPU; `checkpoints/spectralnet/pretrained_ecapa_unnormalized_m26.pt`), and pruning + p_min were re-tuned on AMI dev + Vox val with the warm start on (`results/tuning_vox_warm/`). Tuning chose exactly the same values (p_min 4, relative 0.15/K̂, merge 0.7; same val objective 0.798). VoxConverse test: exact 0.379 → 0.379, ±1 0.608 → 0.612, MAE 1.875 → 1.862, DER 0.077 → 0.077; only 5/232 recordings change K̂ (3 better, 2 worse, all with K ≥ 10); paired ΔMAE −0.013 [−0.043, +0.013], Wilcoxon p = 0.33. AMI test: 0.875 → 0.812 (TS3003a 4 → 3), ΔMAE +0.062 [0, +0.188], p = 0.32. **No significant effect on either corpus**, as on AMI earlier: 500 per-recording fine-tuning steps converge to the same solution whatever the start. The cold-start vox_tuned run stays the reference result.

**Does the gain hold with pyannote VAD?** With pyannote/segmentation-3.0 instead of oracle VAD on AMI test:
`nmesc_ecapa` 0.688 exact / MAE 0.375 (oracle 0.562 / 0.438), `snet_affnet_pp` 0.750 / 0.438 (oracle 0.812 / 0.500).
DER rises (0.127 → 0.169; 0.160 → 0.199) because VAD now adds misses and false alarms. Counting with raw ECAPA gets
*better* with real VAD, plausibly because pyannote drops short and overlapped regions that seed spurious clusters (the
oracle overlap-removal ablation shows the same direction: 0.56 → 0.75). The AffinityNet system keeps its IS1009a
overcount (K̂=7) under real VAD, so its relative advantage on exact accuracy holds but its MAE problem does too.

**Is the AMI improvement statistically meaningful?** Only for `snet_ecapa_pp` vs `nmesc_ecapa` (CI excludes 0, p = 0.025)
— and with n = 16 the power is low. No method beats `baseline_mode` (0.9375), and `baseline_mode` beats `nmesc_ecapa`
significantly (p = 0.034). On AMI test, "4" is the right answer for 15/16 recordings, so AMI alone cannot show a counting
improvement; a method that does well here may just be biased towards 4.

**Other ablation results (table in §3).** sym_norm is worse than unnormalized for raw ECAPA (as in the old project).
The refinement ops help raw ECAPA (test 0.56 → 0.81) but wreck AffinityNet (0.81 → 0.69, DER 0.23): diffusion on an
already-inflated affinity merges everything. Oracle overlap removal (upper bound, uses reference labels) helps raw ECAPA
(0.56 → 0.75), so overlap is a real but partial cause of +1 errors. The old Siamese with only flaws 1–2 fixed collapses
(mean cosine 0.36–0.64 in 64-d, no clear eigengap, K̂ from 1 to 10; 0/16 exact): fixing the two bugs is not enough without
validation, wider output and better pairs.

## 6. Failure analysis (what is left)

| Failure mode | Remaining examples | Where to see it |
|---|---|---|
| A — tiny extra cluster | solved by pruning on raw ECAPA (ES2004a/b, TS3003b/c); TS3003d's 2 % cluster survives `nmesc_ecapa_pp` | `cluster_shares_ami.png` |
| B — one speaker split in two | EN2002a/d with raw ECAPA (5–6 % cluster, gap ratio 1.36/1.65 → 4 is second best); fixed by AffinityNet | `affinity_EN2002a.png`, `spectrum_EN2002a.png` |
| C — dominant cluster swallows others | TS3003a in every method (90–92 % largest cluster; pruning makes it K̂=3) | `affinity_TS3003a.png`, `der_bar_ami.png` |
| D — no clear eigengap / big overcount | AffinityNet on IS1009a (7) and TS3003d (8): true K is the runner-up gap | `spectrum_IS1009a.png`, `spectrum_TS3003d.png`, `scatter_k_ami.png` |
| Model selection on an all-K=4 dev set | AffinityNet epoch pick; ablation ranks reverse between dev and test | `train_curves.png` |
| Speed of SpectralNet | 3.9 min on AMI test (target 3) | `timing.png` |

## 7. Next steps (ranked)

1. **Train and tune on VoxConverse dev** (K = 1–21). This needs `dataset/voxconverse/{audio,rttm}/dev`, which is still
   missing; only test is present. The cross-corpus run (§1b) shows that AMI-only selection does not transfer. Run
   `make-splits`, then `prepare`, then retrain into a new checkpoint folder (keeping `checkpoints/affnet_ami_only`), then retune
   on AMI dev + Vox val.
1b. **Lower bound on p* for short recordings:** p* = 1–2 shatters the graph on the 12 shortest Vox recordings
   (K̂ = 14–24). Add a p_min (absolute, e.g. 3–5, or relative to N) and/or cap K̂ by the number of graph components with at
   least a minimum share. **Tune it on Vox val only**, not on test.
1c. **Make the prune share depend on K or duration** (or tune it on Vox val): 2–3 % from AMI removes real minor
   speakers when K ≥ 8.
2. **Make AffinityNet selection robust:** select on pair EER (smooth) plus count MAE on *speaker-dropout validation
   variants* of AMI dev (K = 1–4), or average the last N epochs / use EMA weights — the current pick is one noisy epoch.
3. **Constrain AffinityNet's cosine scale:** the residual drifted to a space where all cosines are high (mean 0.45);
   add a term that keeps the mean cross-speaker cosine near the ECAPA level, or calibrate (z-normalise) the affinity
   before binarisation. This targets IS1009a/TS3003d.
4. **Tune post-processing on harder validation data** (the same dropout variants), so pruning/merging is not switched
   off just because dev has nothing to fix; use a gap-ratio rule (prefer the runner-up K when the gap ratio < 1.5 and
   the runner-up is smaller) — it would fix EN2002a/d (raw ECAPA) and IS1009a/TS3003d (AffinityNet).
5. **Speed up SpectralNet**: compute the self-check only on a sample of recordings and cap fits at 200 steps; target ≤ 3 min.
6. Optional (Phase 7, not run by decision): a WavLM embedder as an ECAPA alternative.
