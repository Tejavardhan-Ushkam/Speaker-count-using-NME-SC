# baseline_mode — ami / dev

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
| 18 | 1.0000 | 1.0000 | 0.0000 | +0.000 | 1.0000 | 0.0000 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.000], exact [1.000, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 |
|---|---|
| 4 | 18 |

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| nmesc_ecapa | 0.6667 | 0.3889 | +0.333 [+0.111, +0.556] | -0.389 [-0.667, -0.111] | 0.0196 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011a | 4 | 4 | – | – | 0 |
| ES2011b | 4 | 4 | – | – | 0 |
| ES2011c | 4 | 4 | – | – | 0 |
| ES2011d | 4 | 4 | – | – | 0 |
| IB4001 | 4 | 4 | – | – | 0 |

## Per-recording predictions

See `predictions.csv`.
