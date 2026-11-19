# baseline_mode [ami_trained] — voxconverse / test

git commit `f6536655b6e360d377ecb73f941907b2c81816a7-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
| clustering.backend | none |
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
| 232 | 0.0948 | 0.2284 | 3.5560 | -2.478 | 0.0948 | 0.6656 | 0.5000 |

Bootstrap 95 % CI: MAE [3.181, 3.953], exact [0.056, 0.134].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.000 | 0.000 | 3.000 | 3.000 | 0.000 | 3.000 | 3.000 |
| 2 | 31 | 0.000 | 0.000 | 2.000 | 2.000 | 0.000 | 1.000 | 1.000 |
| 3 | 18 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.333 | 0.333 |
| 4 | 22 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 5-7 | 63 | 0.000 | 0.206 | 2.302 | -2.302 | 0.000 | 0.354 | 0.429 |
| 8-12 | 65 | 0.000 | 0.000 | 5.462 | -5.462 | 0.000 | 0.569 | 0.556 |
| 13+ | 18 | 0.000 | 0.000 | 11.111 | -11.111 | 0.000 | 0.730 | 0.733 |

## Confusion (rows K, columns K^)

| K | 4 |
|---|---|
| 1 | 15 |
| 2 | 31 |
| 3 | 18 |
| 4 | 22 |
| 5 | 13 |
| 6 | 18 |
| 7 | 32 |
| 8 | 22 |
| 9 | 15 |
| 10 | 10 |
| 11 | 12 |
| 12 | 6 |
| 13 | 5 |
| 14 | 3 |
| 15 | 6 |
| 17 | 1 |
| 18 | 1 |
| 19 | 1 |
| 21 | 1 |

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| nitgx | 21 | 4 | – | – | 0 |
| vzuru | 19 | 4 | – | – | 0 |
| jeymh | 18 | 4 | – | – | 0 |
| qajyo | 17 | 4 | – | – | 0 |
| byapz | 15 | 4 | – | – | 0 |

## Per-recording predictions

See `predictions.csv`.
