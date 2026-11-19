# snet_affnet_pp — ami / test_pyannote

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
| vad.source | pyannote |
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
| 16 | 0.7500 | 0.8750 | 0.4375 | +0.188 | 0.7500 | 0.1094 | 0.0000 |

Bootstrap 95 % CI: MAE [0.062, 0.875], exact [0.500, 0.938].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.733 | 0.867 | 0.467 | 0.200 | 0.733 | 0.117 | 0.000 |

## Confusion (rows K, columns K^)

| K | 2 | 3 | 4 | 5 | 7 |
|---|---|---|---|---|---|
| 3 | 0 | 1 | 0 | 0 | 0 |
| 4 | 1 | 0 | 11 | 2 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_affnet_pp | 0.1987 | 0.1424 | 0.0124 | 0.0439 | 0.1207 |

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 1 | 0 | 0 | 5 |

## p* distribution

median 5, max 12, hits p_max_abs=60: 0/16

## Timing

clustering total 1.87 min (112.1 s, 7.01 s/recording, max 13.2 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **1.000** (16/16); Ritz-value max rel. error (first k_max+1, excluding λ1): median 9.81e-01, max 5.96e+00 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.076, max 0.218.

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| nmesc_ecapa | 0.6875 | 0.3750 | +0.062 [-0.125, +0.250] | +0.062 [-0.250, +0.500] | 1 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| IS1009a | 4 | 7 | 27 18 16 14 13 6 5 | 1.28 | 9 |
| TS3003a | 4 | 2 | 91 9 | 1.13 | 4 |
| EN2002d | 4 | 5 | 28 25 22 13 12 | 1.21 | 7 |
| TS3003d | 4 | 5 | 55 17 14 8 6 | 1.60 | 9 |
| EN2002a | 4 | 4 | 37 25 22 16 | 3.17 | 3 |

## Per-recording predictions

See `predictions.csv`.
