## 4. Success criteria (prompt §10) — AMI only

| Metric | Old best | Target for `snet_affnet_pp` | Result | Met? |
|---|---|---|---|---|
| AMI test exact | 0.5625 | ≥ 0.80, and compared against "always 4" (0.9375) | **0.8125**; always-4 = 0.9375 | ≥ 0.80 yes; **below the always-4 baseline** |
| AMI test MAE | 0.4375 | ≤ 0.25 | **0.500** | **no** — two large overcounts (IS1009a K̂=7, TS3003d K̂=8) |
| VoxConverse MAE / rel. acc | – | ≥ 20 % MAE reduction vs `nmesc_ecapa` | not measurable | VoxConverse data unavailable |
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
`snet_affnet_pp` give the same K̂ as `nmesc_affnet` (the no-op warnings below are expected, not bugs) — and why nothing
caught the IS1009a/TS3003d overcounts on test.

**How does the error depend on true K (VoxConverse)?** Not measurable: VoxConverse is not available, and AMI has only
K=3 (1 recording, always right) and K=4. This is the central gap of this evaluation (see Next steps 1).

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

1. **Add VoxConverse** (K = 1–21). It is required by the plan for training, tuning and testing, and AMI alone cannot
   distinguish counting skill from "always 4". The code is ready: `make-splits`, `prepare`, then rerun `run_all.sh`.
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
