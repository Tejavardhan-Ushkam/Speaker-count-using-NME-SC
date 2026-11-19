# nmesc_affnet [bce_only] — ami / test

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
| 16 | 0.8750 | 1.0000 | 0.1250 | +0.125 | 0.8750 | 0.0312 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.312], exact [0.688, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.867 | 1.000 | 0.133 | 0.133 | 0.867 | 0.033 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 |
|---|---|---|---|
| 3 | 1 | 0 | 0 |
| 4 | 0 | 13 | 2 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [bce_only] | 0.1270 | 0.1052 | 0.0000 | 0.0218 | 0.0442 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 2 | 1 | 0 | 0 | 3 |

## p* distribution

median 5, max 9, hits p_max_abs=60: 0/16

## Timing

clustering total 1.31 min (78.5 s, 4.90 s/recording, max 15.9 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.062 [-0.250, +0.125] | +0.062 [-0.125, +0.250] | 0.564 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.312 [+0.125, +0.562] | -0.312 [-0.562, -0.125] | 0.0253 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| EN2002a | 4 | 5 | 37 20 18 16 9 | 1.16 | 5 |
| TS3003d | 4 | 5 | 57 16 13 12 3 | 2.06 | 9 |
| EN2002b | 4 | 4 | 45 24 18 13 | 2.06 | 3 |
| EN2002c | 3 | 3 | 40 31 29 | 2.34 | 4 |
| EN2002d | 4 | 4 | 38 25 23 14 | 1.49 | 3 |

## Per-recording predictions

See `predictions.csv`.
