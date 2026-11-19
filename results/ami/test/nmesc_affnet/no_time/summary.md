# nmesc_affnet [no_time] — ami / test

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
| 16 | 1.0000 | 1.0000 | 0.0000 | +0.000 | 1.0000 | 0.0000 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.000], exact [1.000, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 |
|---|---|---|
| 3 | 1 | 0 |
| 4 | 0 | 15 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [no_time] | 0.1290 | 0.1052 | 0.0000 | 0.0237 | 0.0461 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 1 | 1 | 0 | 0 | 3 |

## p* distribution

median 3, max 6, hits p_max_abs=60: 0/16

## Timing

clustering total 0.83 min (49.5 s, 3.10 s/recording, max 8.9 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | +0.062 [+0.000, +0.188] | -0.062 [-0.188, +0.000] | 0.317 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.438 [+0.188, +0.688] | -0.438 [-0.688, -0.188] | 0.00815 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| EN2002a | 4 | 4 | 39 23 22 16 | 2.29 | 3 |
| EN2002b | 4 | 4 | 39 24 23 14 | 1.73 | 3 |
| EN2002c | 3 | 3 | 43 30 27 | 4.61 | 3 |
| EN2002d | 4 | 4 | 33 31 22 14 | 1.46 | 5 |
| ES2004a | 4 | 4 | 45 30 13 13 | 1.94 | 3 |

## Per-recording predictions

See `predictions.csv`.
