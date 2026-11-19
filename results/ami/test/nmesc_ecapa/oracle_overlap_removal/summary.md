# nmesc_ecapa [oracle_overlap_removal] — ami / test

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
| affinity.refine | False |
| affinity.oracle_overlap_removal (ORACLE) | True |
| postprocess.enabled | False |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.7500 | 1.0000 | 0.2500 | +0.250 | 0.7500 | 0.0625 | 0.0000 |

Bootstrap 95 % CI: MAE [0.062, 0.500], exact [0.500, 0.938].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.733 | 1.000 | 0.267 | 0.267 | 0.733 | 0.067 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 |
|---|---|---|---|
| 3 | 1 | 0 | 0 |
| 4 | 0 | 11 | 4 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa [oracle_overlap_removal] | 0.1234 | 0.1052 | 0.0000 | 0.0181 | 0.0412 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 4 | 1 | 0 | 0 | 1 |

## p* distribution

median 6, max 12, hits p_max_abs=60: 0/16

## Timing

clustering total 0.41 min (24.7 s, 1.54 s/recording, max 2.6 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.188 [-0.438, +0.062] | +0.188 [-0.062, +0.438] | 0.18 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.188 [+0.000, +0.375] | -0.188 [-0.375, +0.000] | 0.0833 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2004a | 4 | 5 | 50 25 14 9 2 | 3.11 | 9 |
| ES2004b | 4 | 5 | 31 29 26 14 1 | 2.99 | 3 |
| TS3003c | 4 | 5 | 35 29 24 11 2 | 1.84 | 12 |
| TS3003d | 4 | 5 | 56 16 14 11 3 | 3.63 | 4 |
| EN2002a | 4 | 4 | 46 22 19 13 | 1.99 | 3 |

## Per-recording predictions

See `predictions.csv`.
