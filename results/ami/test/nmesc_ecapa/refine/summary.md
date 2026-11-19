# nmesc_ecapa [refine] — ami / test

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
| clustering.backend | exact |
| clustering.laplacian | unnormalized |
| clustering.k_max | 10 |
| clustering.p_max_abs | 60 |
| clustering.coarse_to_fine | True |
| clustering.eig_solver | sparse |
| vad.source | oracle |
| affinity.refine | True |
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | False |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.8125 | 0.9375 | 0.2500 | -0.125 | 0.8125 | 0.0625 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.562], exact [0.625, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.800 | 0.933 | 0.267 | -0.133 | 0.800 | 0.067 | 0.000 |

## Confusion (rows K, columns K^)

| K | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| 3 | 0 | 1 | 0 | 0 |
| 4 | 1 | 1 | 12 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa [refine] | 0.1250 | 0.1052 | 0.0000 | 0.0198 | 0.0443 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 2 |

## p* distribution

median 52, max 60, hits p_max_abs=60: 5/16  **(often at the cap: raise p_max_abs)**

## Timing

clustering total 0.68 min (41.0 s, 2.56 s/recording, max 7.6 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.125 [-0.375, +0.125] | +0.188 [-0.125, +0.500] | 0.257 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.250 [-0.062, +0.562] | -0.188 [-0.562, +0.250] | 0.366 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| TS3003a | 4 | 2 | 94 6 | 1.34 | 47 |
| EN2002d | 4 | 5 | 36 26 25 11 2 | 2.17 | 23 |
| IS1009a | 4 | 3 | 69 19 12 | 5.27 | 59 |
| EN2002a | 4 | 4 | 41 22 19 18 | 1.49 | 60 |
| EN2002b | 4 | 4 | 45 24 18 13 | 5.09 | 60 |

## Per-recording predictions

See `predictions.csv`.
