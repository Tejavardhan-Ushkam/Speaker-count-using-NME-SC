# snet_ecapa_pp [vox_warm] — ami / test

git commit `582a65b989a5ea57512b7456ad0b40386e6260ac`; resolved config in `config_resolved.yaml`.

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
| postprocess.min_cluster_share (used) | 0.15 |
| postprocess.merge_threshold (used) | 0.7 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.share_mode (used) | relative |
| postprocess.p_min (used) | 4 |
| postprocess.source (used) | results/tuning_vox_warm/snet_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.8125 | 1.0000 | 0.1875 | +0.062 | 0.8125 | 0.0469 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.375], exact [0.625, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.800 | 1.000 | 0.200 | 0.067 | 0.800 | 0.050 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 |
|---|---|---|---|
| 3 | 1 | 0 | 0 |
| 4 | 1 | 12 | 2 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_ecapa_pp [vox_warm] | 0.1284 | 0.1052 | 0.0000 | 0.0232 | 0.0439 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 1 | 0 | 0 | 3 |

## p* distribution

median 5, max 8, hits p_max_abs=60: 0/16

## Timing

clustering total 1.94 min (116.2 s, 7.26 s/recording, max 16.4 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **1.000** (16/16); Ritz-value max rel. error (first k_max+1, excluding λ1): median 4.16e-01, max 1.35e+00 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.033, max 0.128.

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.125 [-0.375, +0.125] | +0.125 [-0.125, +0.375] | 0.317 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.250 [+0.000, +0.500] | -0.250 [-0.500, +0.000] | 0.102 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| EN2002a | 4 | 5 | 37 20 18 17 8 | 1.43 | 5 |
| EN2002d | 4 | 5 | 32 25 23 11 9 | 1.72 | 4 |
| TS3003a | 4 | 3 | 85 8 6 | 1.27 | 5 |
| EN2002b | 4 | 4 | 41 24 20 15 | 1.80 | 4 |
| EN2002c | 3 | 3 | 40 31 30 | 2.26 | 6 |

## Per-recording predictions

See `predictions.csv`.
