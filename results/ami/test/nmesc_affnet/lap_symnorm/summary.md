# nmesc_affnet [lap_symnorm] — ami / test

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | affnet |
| clustering.backend | exact |
| clustering.laplacian | sym_norm |
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
| 16 | 0.8125 | 0.8750 | 0.3750 | +0.250 | 0.8125 | 0.0938 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.812], exact [0.625, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.800 | 0.867 | 0.400 | 0.267 | 0.800 | 0.100 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 6 | 7 |
|---|---|---|---|---|
| 3 | 1 | 0 | 0 | 0 |
| 4 | 1 | 12 | 1 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [lap_symnorm] | 0.1480 | 0.1052 | 0.0000 | 0.0427 | 0.0673 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 3 | 1 | 0 | 0 | 2 |

## p* distribution

median 5, max 23, hits p_max_abs=60: 0/16

## Timing

clustering total 0.88 min (52.7 s, 3.30 s/recording, max 10.4 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.125 [-0.375, +0.125] | +0.312 [-0.062, +0.812] | 0.197 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.250 [-0.062, +0.562] | -0.062 [-0.500, +0.500] | 0.564 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| IS1009a | 4 | 7 | 37 26 18 8 5 4 2 | 1.85 | 11 |
| TS3003d | 4 | 6 | 58 15 13 7 4 3 | 1.44 | 23 |
| TS3003a | 4 | 3 | 92 6 2 | 1.60 | 5 |
| EN2002a | 4 | 4 | 37 23 22 17 | 2.28 | 5 |
| EN2002b | 4 | 4 | 40 23 23 13 | 1.80 | 5 |

## Per-recording predictions

See `predictions.csv`.
