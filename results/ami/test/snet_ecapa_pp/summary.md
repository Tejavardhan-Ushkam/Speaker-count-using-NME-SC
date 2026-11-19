# snet_ecapa_pp — ami / test

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
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
| postprocess.min_cluster_share (used) | 0.03 |
| postprocess.merge_threshold (used) | 0.6 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.source (used) | results/tuning/snet_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.8750 | 1.0000 | 0.1250 | +0.125 | 0.8750 | 0.0312 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.312], exact [0.688, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.867 | 1.000 | 0.133 | 0.133 | 0.867 | 0.033 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 |
|---|---|---|---|
| 3 | 1 | 0 | 0 |
| 4 | 0 | 13 | 2 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_ecapa_pp | 0.1284 | 0.1052 | 0.0000 | 0.0231 | 0.0439 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 1 | 0 | 0 | 2 |

## p* distribution

median 6, max 18, hits p_max_abs=60: 0/16

## Timing

clustering total 4.08 min (245.1 s, 15.32 s/recording, max 29.0 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **1.000** (16/16); Ritz-value max rel. error (first k_max+1, excluding λ1): median 3.72e-01, max 2.48e+00 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.024, max 0.128.

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.062 [-0.250, +0.125] | +0.062 [-0.125, +0.250] | 0.564 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.312 [+0.125, +0.562] | -0.312 [-0.562, -0.125] | 0.0253 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| EN2002a | 4 | 5 | 37 20 18 17 8 | 1.43 | 5 |
| EN2002d | 4 | 5 | 32 25 23 11 9 | 1.72 | 4 |
| EN2002b | 4 | 4 | 41 24 20 15 | 1.80 | 4 |
| EN2002c | 3 | 3 | 40 31 30 | 2.26 | 6 |
| ES2004a | 4 | 4 | 44 31 15 10 | 5.34 | 5 |

## Per-recording predictions

See `predictions.csv`.
