# nmesc_affnet [ctx0] — ami / test

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | affnet |
| clustering.backend | exact |
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
| 16 | 0.8125 | 0.8750 | 0.3125 | +0.062 | 0.8125 | 0.0781 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.688], exact [0.625, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.800 | 0.867 | 0.333 | 0.067 | 0.800 | 0.083 | 0.000 |

## Confusion (rows K, columns K^)

| K | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| 3 | 0 | 1 | 0 | 0 | 0 |
| 4 | 1 | 0 | 12 | 1 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [ctx0] | 0.1305 | 0.1052 | 0.0000 | 0.0253 | 0.0489 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 2 | 1 | 0 | 0 | 1 |

## p* distribution

median 4, max 7, hits p_max_abs=60: 0/16

## Timing

clustering total 1.32 min (79.5 s, 4.97 s/recording, max 17.0 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.125 [-0.375, +0.125] | +0.250 [-0.062, +0.625] | 0.194 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.250 [-0.062, +0.562] | -0.125 [-0.500, +0.312] | 0.564 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| TS3003a | 4 | 2 | 94 6 | 3.22 | 2 |
| TS3003d | 4 | 6 | 58 15 14 7 4 3 | 1.04 | 5 |
| IS1009a | 4 | 5 | 71 18 5 4 2 | 1.53 | 4 |
| EN2002a | 4 | 4 | 36 24 22 18 | 3.19 | 5 |
| EN2002b | 4 | 4 | 41 23 21 15 | 3.35 | 6 |

## Per-recording predictions

See `predictions.csv`.
