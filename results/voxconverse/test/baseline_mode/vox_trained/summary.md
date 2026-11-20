# baseline_mode [vox_trained] — voxconverse / test

git commit `3d875af9e0076f603863f592ff6fcc5a8b8d0801`; resolved config in `config_resolved.yaml`.

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
| 232 | 0.1336 | 0.2759 | 4.6078 | -4.478 | 0.1336 | 0.6087 | 0.7143 |

Bootstrap 95 % CI: MAE [4.134, 5.112], exact [0.091, 0.181].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 1.000 | 1.000 |
| 2 | 31 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 3 | 18 | 0.000 | 1.000 | 1.000 | -1.000 | 0.000 | 0.333 | 0.333 |
| 4 | 22 | 0.000 | 0.000 | 2.000 | -2.000 | 0.000 | 0.500 | 0.500 |
| 5-7 | 63 | 0.000 | 0.000 | 4.302 | -4.302 | 0.000 | 0.677 | 0.714 |
| 8-12 | 65 | 0.000 | 0.000 | 7.462 | -7.462 | 0.000 | 0.784 | 0.778 |
| 13+ | 18 | 0.000 | 0.000 | 13.111 | -13.111 | 0.000 | 0.865 | 0.867 |

## Confusion (rows K, columns K^)

| K | 2 |
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
| nitgx | 21 | 2 | – | – | 0 |
| vzuru | 19 | 2 | – | – | 0 |
| jeymh | 18 | 2 | – | – | 0 |
| qajyo | 17 | 2 | – | – | 0 |
| byapz | 15 | 2 | – | – | 0 |

## Per-recording predictions

See `predictions.csv`.
