# snet_affnet_pp — ami / dev

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | affnet |
| clustering.backend | spectralnet |
| clustering.laplacian | unnormalized |
| clustering.k_max | 10 |
| clustering.p_max_abs | 60 |
| clustering.coarse_to_fine | True |
| clustering.eig_solver | sparse |
| vad.source | oracle |
| affinity.refine | False |
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | True |
| postprocess.min_cluster_share (used) | 0.0 |
| postprocess.merge_threshold (used) | None |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.source (used) | results/tuning/snet_affnet_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 18 | 1.0000 | 1.0000 | 0.0000 | +0.000 | 1.0000 | 0.0000 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.000], exact [1.000, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 |
|---|---|
| 4 | 18 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_affnet_pp | 0.1251 | 0.1065 | 0.0000 | 0.0187 | 0.0526 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 4 |

## p* distribution

median 4, max 9, hits p_max_abs=60: 0/18

## Timing

clustering total 3.96 min (237.6 s, 13.20 s/recording, max 22.0 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **1.000** (18/18); Ritz-value max rel. error (first k_max+1, excluding λ1): median 1.07e+00, max 2.22e+00 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.087, max 0.213.

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | 1 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.333 [+0.111, +0.556] | -0.389 [-0.667, -0.111] | 0.0196 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011a | 4 | 4 | 49 27 20 4 | 1.44 | 3 |
| ES2011b | 4 | 4 | 29 27 26 18 | 6.04 | 4 |
| ES2011c | 4 | 4 | 34 25 22 19 | 3.44 | 4 |
| ES2011d | 4 | 4 | 35 27 20 18 | 1.44 | 6 |
| IB4001 | 4 | 4 | 53 33 9 5 | 1.38 | 5 |

## Per-recording predictions

See `predictions.csv`.
