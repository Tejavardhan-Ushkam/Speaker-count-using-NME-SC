# nmesc_ecapa — ami / test

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
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | False |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.5625 | 1.0000 | 0.4375 | +0.438 | 0.5625 | 0.1094 | 0.0000 |

Bootstrap 95 % CI: MAE [0.188, 0.688], exact [0.312, 0.812].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.533 | 1.000 | 0.467 | 0.467 | 0.533 | 0.117 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 |
|---|---|---|---|
| 3 | 1 | 0 | 0 |
| 4 | 0 | 8 | 7 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa | 0.1269 | 0.1052 | 0.0000 | 0.0217 | 0.0431 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 6 | 1 | 0 | 0 | 2 |

## p* distribution

median 6, max 18, hits p_max_abs=60: 0/16

## Timing

clustering total 1.32 min (79.4 s, 4.96 s/recording, max 18.6 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.375 [-0.688, -0.062] | +0.375 [+0.062, +0.688] | 0.0339 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| EN2002a | 4 | 5 | 39 21 18 17 5 | 1.36 | 5 |
| EN2002d | 4 | 5 | 33 25 24 11 6 | 1.65 | 4 |
| ES2004a | 4 | 5 | 44 30 14 10 2 | 5.37 | 5 |
| ES2004b | 4 | 5 | 34 28 24 13 1 | 1.99 | 3 |
| TS3003b | 4 | 5 | 43 30 17 10 0 | 1.78 | 4 |

## Per-recording predictions

See `predictions.csv`.
