# snet_affnet_pp — ami / test

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
| 16 | 0.8125 | 0.8750 | 0.5000 | +0.375 | 0.8125 | 0.1250 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 1.125], exact [0.625, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.800 | 0.867 | 0.533 | 0.400 | 0.800 | 0.133 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 7 | 8 |
|---|---|---|---|---|
| 3 | 1 | 0 | 0 | 0 |
| 4 | 1 | 12 | 1 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_affnet_pp | 0.1602 | 0.1052 | 0.0000 | 0.0550 | 0.0796 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 2 |

## p* distribution

median 4, max 12, hits p_max_abs=60: 0/16

## Timing

clustering total 3.85 min (231.0 s, 14.44 s/recording, max 24.5 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **1.000** (16/16); Ritz-value max rel. error (first k_max+1, excluding λ1): median 1.18e+00, max 3.61e+00 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.110, max 0.220.

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.125 [-0.375, +0.125] | +0.438 [-0.062, +1.062] | 0.197 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.250 [-0.062, +0.562] | +0.062 [-0.500, +0.750] | 0.851 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| TS3003d | 4 | 8 | 48 16 13 6 5 4 4 2 | 1.52 | 4 |
| IS1009a | 4 | 7 | 23 19 18 16 12 7 5 | 1.32 | 12 |
| TS3003a | 4 | 3 | 89 6 5 | 1.90 | 3 |
| EN2002a | 4 | 4 | 36 24 23 17 | 2.27 | 5 |
| EN2002b | 4 | 4 | 39 24 23 14 | 1.78 | 5 |

## Per-recording predictions

See `predictions.csv`.
