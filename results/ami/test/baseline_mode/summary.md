# baseline_mode — ami / test

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
| clustering.backend | none |
| clustering.laplacian | unnormalized |
| clustering.k_max | 10 |
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
| 16 | 0.9375 | 1.0000 | 0.0625 | +0.062 | 0.9375 | 0.0208 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.188], exact [0.812, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 0.000 | 1.000 | 1.000 | 1.000 | 0.000 | 0.333 | 0.333 |
| 4 | 15 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 |
|---|---|
| 3 | 1 |
| 4 | 15 |

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| nmesc_ecapa | 0.5625 | 0.4375 | +0.375 [+0.062, +0.688] | -0.375 [-0.688, -0.062] | 0.0339 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| EN2002c | 3 | 4 | – | – | 0 |
| EN2002a | 4 | 4 | – | – | 0 |
| EN2002b | 4 | 4 | – | – | 0 |
| EN2002d | 4 | 4 | – | – | 0 |
| ES2004a | 4 | 4 | – | – | 0 |

## Per-recording predictions

See `predictions.csv`.
