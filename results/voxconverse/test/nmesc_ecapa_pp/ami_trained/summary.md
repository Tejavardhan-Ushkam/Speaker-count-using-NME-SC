# nmesc_ecapa_pp [ami_trained] — voxconverse / test

git commit `f6536655b6e360d377ecb73f941907b2c81816a7-dirty`; resolved config in `config_resolved.yaml`.

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
| postprocess.min_cluster_share (used) | 0.02 |
| postprocess.merge_threshold (used) | 0.6 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.source (used) | results/tuning_ami_only/nmesc_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 232 | 0.3578 | 0.5388 | 2.0862 | -1.776 | 0.4353 | 0.3057 | 0.2500 |

Bootstrap 95 % CI: MAE [1.776, 2.405], exact [0.297, 0.418].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.667 | 0.867 | 0.800 | 0.800 | 0.667 | 0.800 | 0.000 |
| 2 | 31 | 0.839 | 0.935 | 0.290 | 0.097 | 0.839 | 0.145 | 0.000 |
| 3 | 18 | 0.611 | 0.778 | 0.778 | 0.000 | 0.611 | 0.259 | 0.000 |
| 4 | 22 | 0.409 | 0.773 | 0.818 | -0.455 | 0.409 | 0.205 | 0.250 |
| 5-7 | 63 | 0.349 | 0.571 | 1.444 | -1.222 | 0.460 | 0.227 | 0.167 |
| 8-12 | 65 | 0.077 | 0.231 | 3.354 | -3.354 | 0.231 | 0.352 | 0.375 |
| 13+ | 18 | 0.000 | 0.056 | 6.778 | -6.778 | 0.056 | 0.449 | 0.400 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 14 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | 3 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 2 | 3 | 26 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 2 | 3 | 11 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 0 | 4 | 6 | 9 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 0 | 1 | 2 | 2 | 5 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| 6 | 0 | 1 | 0 | 5 | 4 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 1 | 2 | 2 | 5 | 6 | 6 | 9 | 1 | 0 | 0 | 0 | 0 | 0 |
| 8 | 1 | 0 | 1 | 6 | 5 | 2 | 4 | 3 | 0 | 0 | 0 | 0 | 0 |
| 9 | 0 | 0 | 3 | 3 | 2 | 2 | 1 | 3 | 1 | 0 | 0 | 0 | 0 |
| 10 | 0 | 0 | 0 | 1 | 0 | 3 | 1 | 2 | 2 | 1 | 0 | 0 | 0 |
| 11 | 0 | 0 | 2 | 0 | 1 | 1 | 2 | 4 | 1 | 1 | 0 | 0 | 0 |
| 12 | 0 | 0 | 0 | 0 | 0 | 1 | 4 | 1 | 0 | 0 | 0 | 0 | 0 |
| 13 | 0 | 1 | 0 | 0 | 2 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 0 |
| 15 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 1 | 0 | 1 |
| 17 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa_pp [ami_trained] | 0.0791 | 0.0434 | 0.0000 | 0.0356 | 0.0591 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 67 | 41 | 0 | 0 | 20 |

## p* distribution

median 5, max 55, hits p_max_abs=60: 0/232

## Timing

clustering total 4.92 min (294.9 s, 1.27 s/recording, max 6.8 s)

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| eqsta | 15 | 3 | 52 43 5 | 1.82 | 6 |
| jeymh | 18 | 6 | 28 23 19 17 11 2 | 1.70 | 11 |
| pwnsw | 13 | 2 | 75 25 | 2.53 | 7 |
| qajyo | 17 | 7 | 47 18 9 9 9 4 3 | 2.12 | 9 |
| nitgx | 21 | 12 | 53 6 6 5 5 5 4 4 4 3 3 2 | 1.95 | 8 |

## Per-recording predictions

See `predictions.csv`.
