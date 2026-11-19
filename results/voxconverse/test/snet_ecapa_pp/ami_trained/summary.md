# snet_ecapa_pp [ami_trained] — voxconverse / test

git commit `f6536655b6e360d377ecb73f941907b2c81816a7-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
| clustering.backend | spectralnet |
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
| postprocess.merge_threshold (used) | 0.6 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.source (used) | results/tuning_ami_only/snet_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 232 | 0.3017 | 0.4957 | 2.5431 | -2.284 | 0.3707 | 0.3456 | 0.2857 |

Bootstrap 95 % CI: MAE [2.194, 2.918], exact [0.246, 0.362].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.733 | 0.867 | 0.733 | 0.733 | 0.733 | 0.733 | 0.000 |
| 2 | 31 | 0.806 | 0.968 | 0.290 | 0.097 | 0.806 | 0.145 | 0.000 |
| 3 | 18 | 0.667 | 0.833 | 0.611 | -0.167 | 0.667 | 0.204 | 0.000 |
| 4 | 22 | 0.364 | 0.818 | 0.818 | -0.545 | 0.364 | 0.205 | 0.250 |
| 5-7 | 63 | 0.190 | 0.492 | 1.825 | -1.635 | 0.349 | 0.285 | 0.286 |
| 8-12 | 65 | 0.031 | 0.123 | 4.200 | -4.200 | 0.123 | 0.438 | 0.455 |
| 13+ | 18 | 0.000 | 0.000 | 8.500 | -8.500 | 0.000 | 0.561 | 0.602 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 11 | 2 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| 2 | 3 | 25 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 3 | 2 | 3 | 12 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 4 | 0 | 4 | 7 | 8 | 3 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 0 | 1 | 2 | 4 | 3 | 1 | 2 | 0 | 0 | 0 | 0 |
| 6 | 0 | 2 | 2 | 4 | 4 | 6 | 0 | 0 | 0 | 0 | 0 |
| 7 | 1 | 2 | 4 | 7 | 5 | 9 | 3 | 1 | 0 | 0 | 0 |
| 8 | 1 | 0 | 3 | 6 | 5 | 3 | 2 | 2 | 0 | 0 | 0 |
| 9 | 0 | 0 | 6 | 2 | 1 | 1 | 1 | 4 | 0 | 0 | 0 |
| 10 | 0 | 0 | 1 | 0 | 4 | 3 | 1 | 1 | 0 | 0 | 0 |
| 11 | 0 | 0 | 2 | 0 | 3 | 2 | 2 | 2 | 1 | 0 | 0 |
| 12 | 0 | 0 | 2 | 1 | 0 | 0 | 3 | 0 | 0 | 0 | 0 |
| 13 | 0 | 1 | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 0 | 0 |
| 14 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| 15 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 2 | 1 | 1 | 0 |
| 17 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_ecapa_pp [ami_trained] | 0.0901 | 0.0434 | 0.0000 | 0.0467 | 0.0705 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 40 | 0 | 0 | 21 |

## p* distribution

median 5, max 55, hits p_max_abs=60: 0/232

## Timing

clustering total 11.55 min (693.0 s, 2.99 s/recording, max 9.4 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **1.000** (232/232); Ritz-value max rel. error (first k_max+1, excluding λ1): median 4.56e+00, max 6.20e+03 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.004, max 0.169.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| jeymh | 18 | 5 | 27 23 19 18 13 | 1.71 | 11 |
| nitgx | 21 | 8 | 52 9 7 7 7 6 6 5 | 1.99 | 8 |
| eqsta | 15 | 3 | 52 43 5 | 1.81 | 6 |
| pwnsw | 13 | 2 | 74 26 | 2.51 | 7 |
| byapz | 15 | 5 | 75 8 8 5 5 | 4.49 | 7 |

## Per-recording predictions

See `predictions.csv`.
