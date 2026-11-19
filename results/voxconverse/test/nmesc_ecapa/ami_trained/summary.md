# nmesc_ecapa [ami_trained] — voxconverse / test

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
| postprocess.enabled | False |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 232 | 0.4095 | 0.5948 | 2.3534 | -0.198 | 0.5086 | 0.6967 | 0.1429 |

Bootstrap 95 % CI: MAE [1.849, 2.892], exact [0.349, 0.474].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.533 | 0.600 | 4.800 | 4.800 | 0.533 | 4.800 | 0.000 |
| 2 | 31 | 0.839 | 0.903 | 1.323 | 1.194 | 0.839 | 0.661 | 0.000 |
| 3 | 18 | 0.500 | 0.722 | 3.667 | 3.111 | 0.500 | 1.222 | 0.167 |
| 4 | 22 | 0.545 | 0.818 | 1.455 | 0.545 | 0.545 | 0.364 | 0.000 |
| 5-7 | 63 | 0.429 | 0.635 | 1.619 | -0.349 | 0.524 | 0.272 | 0.143 |
| 8-12 | 65 | 0.185 | 0.369 | 2.492 | -2.062 | 0.369 | 0.264 | 0.250 |
| 13+ | 18 | 0.056 | 0.333 | 3.944 | -3.722 | 0.333 | 0.268 | 0.249 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 18 | 19 | 20 | 21 | 23 | 24 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 |
| 2 | 2 | 26 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 |
| 3 | 1 | 3 | 9 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 |
| 4 | 0 | 3 | 4 | 12 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 5 | 0 | 1 | 2 | 1 | 6 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| 6 | 0 | 1 | 0 | 2 | 5 | 9 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 0 | 1 | 4 | 2 | 4 | 6 | 12 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8 | 1 | 0 | 0 | 3 | 3 | 5 | 2 | 6 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 | 0 | 0 | 2 | 2 | 0 | 3 | 3 | 0 | 3 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 10 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 1 | 2 | 2 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11 | 0 | 0 | 2 | 0 | 0 | 2 | 2 | 2 | 1 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 13 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 15 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa [ami_trained] | 0.1246 | 0.0434 | 0.0000 | 0.0812 | 0.1060 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 102 | 33 | 0 | 0 | 20 |

## p* distribution

median 5, max 55, hits p_max_abs=60: 0/232

## Timing

clustering total 4.94 min (296.3 s, 1.28 s/recording, max 6.8 s)

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| wdvva | 2 | 23 | 8 7 7 7 5 5 5 5 5 4 4 4 4 4 3 3 3 3 3 3 3 3 3 | 1.94 | 1 |
| xkmqx | 3 | 24 | 7 5 5 5 5 5 5 5 5 5 5 3 3 3 3 3 3 3 3 3 3 3 3 3 | 1.09 | 1 |
| msbyq | 4 | 24 | 7 7 5 5 5 5 5 5 5 5 5 5 5 5 5 2 2 2 2 2 2 2 2 2 | 1.02 | 1 |
| vylyk | 3 | 23 | 9 8 7 7 5 5 5 5 5 4 4 4 4 4 3 3 3 3 3 3 3 3 3 | 1.49 | 1 |
| neiye | 1 | 20 | 7 7 7 7 7 7 5 5 5 5 5 5 3 3 3 3 3 3 3 3 | 1.40 | 1 |

## Per-recording predictions

See `predictions.csv`.
