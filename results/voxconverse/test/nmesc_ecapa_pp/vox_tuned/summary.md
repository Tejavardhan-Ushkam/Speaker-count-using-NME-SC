# nmesc_ecapa_pp [vox_tuned] — voxconverse / test

git commit `3d875af9e0076f603863f592ff6fcc5a8b8d0801`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
| clustering.backend | exact |
| clustering.laplacian | unnormalized |
| clustering.k_max | 25 |
| clustering.p_max_abs | 60 |
| clustering.coarse_to_fine | True |
| clustering.eig_solver | sparse |
| vad.source | oracle |
| affinity.refine | False |
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | True |
| postprocess.min_cluster_share (used) | 0.03 |
| postprocess.merge_threshold (used) | 0.7 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.share_mode (used) | absolute |
| postprocess.p_min (used) | 4 |
| postprocess.source (used) | results/tuning_vox/nmesc_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 232 | 0.3233 | 0.5172 | 2.5043 | -2.435 | 0.4009 | 0.2951 | 0.2500 |

Bootstrap 95 % CI: MAE [2.142, 2.884], exact [0.263, 0.384].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.867 | 1.000 | 0.133 | 0.133 | 0.867 | 0.133 | 0.000 |
| 2 | 31 | 0.903 | 1.000 | 0.097 | -0.032 | 0.903 | 0.048 | 0.000 |
| 3 | 18 | 0.556 | 0.778 | 0.667 | -0.667 | 0.556 | 0.222 | 0.000 |
| 4 | 22 | 0.364 | 0.818 | 0.818 | -0.636 | 0.364 | 0.205 | 0.250 |
| 5-7 | 63 | 0.222 | 0.540 | 1.746 | -1.651 | 0.413 | 0.272 | 0.200 |
| 8-12 | 65 | 0.031 | 0.123 | 4.354 | -4.354 | 0.123 | 0.451 | 0.500 |
| 13+ | 18 | 0.000 | 0.000 | 8.500 | -8.500 | 0.000 | 0.559 | 0.538 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 2 | 28 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 4 | 4 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 0 | 4 | 8 | 8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 0 | 1 | 2 | 5 | 4 | 0 | 1 | 0 | 0 | 0 | 0 |
| 6 | 0 | 2 | 2 | 4 | 3 | 7 | 0 | 0 | 0 | 0 | 0 |
| 7 | 1 | 2 | 4 | 7 | 3 | 11 | 3 | 1 | 0 | 0 | 0 |
| 8 | 1 | 0 | 3 | 4 | 6 | 3 | 3 | 2 | 0 | 0 | 0 |
| 9 | 0 | 0 | 7 | 1 | 1 | 1 | 2 | 3 | 0 | 0 | 0 |
| 10 | 1 | 0 | 0 | 1 | 4 | 2 | 1 | 1 | 0 | 0 | 0 |
| 11 | 0 | 0 | 2 | 2 | 4 | 0 | 2 | 1 | 1 | 0 | 0 |
| 12 | 0 | 0 | 2 | 1 | 0 | 1 | 2 | 0 | 0 | 0 | 0 |
| 13 | 0 | 1 | 0 | 0 | 1 | 2 | 0 | 1 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| 15 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 1 | 1 | 0 |
| 17 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| 21 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa_pp [vox_tuned] | 0.0886 | 0.0434 | 0.0000 | 0.0452 | 0.0694 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 43 | 0 | 0 | 22 |

## p* distribution

median 5, max 55, hits p_max_abs=60: 0/232

## Timing

clustering total 4.70 min (282.3 s, 1.22 s/recording, max 6.6 s)

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| nitgx | 21 | 7 | 55 10 9 8 7 7 5 | 1.14 | 4 |
| jeymh | 18 | 5 | 28 23 19 17 13 | 2.01 | 4 |
| eqsta | 15 | 3 | 52 43 5 | 1.82 | 6 |
| pwnsw | 13 | 2 | 75 25 | 2.53 | 7 |
| byapz | 15 | 5 | 77 8 7 5 4 | 4.48 | 7 |

## Per-recording predictions

See `predictions.csv`.
