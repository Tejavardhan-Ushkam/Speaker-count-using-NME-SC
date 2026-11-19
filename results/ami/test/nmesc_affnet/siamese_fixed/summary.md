# nmesc_affnet [siamese_fixed] — ami / test

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | siamese |
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
| 16 | 0.0000 | 0.0625 | 2.9375 | -0.812 | 0.0000 | 0.7448 | 0.7500 |

Bootstrap 95 % CI: MAE [2.375, 3.625], exact [0.000, 0.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 0.000 | 0.000 | 2.000 | -2.000 | 0.000 | 0.667 | 0.667 |
| 4 | 15 | 0.000 | 0.067 | 3.000 | -0.733 | 0.000 | 0.750 | 0.750 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 6 | 7 | 10 |
|---|---|---|---|---|---|---|
| 3 | 1 | 0 | 0 | 0 | 0 | 0 |
| 4 | 7 | 3 | 1 | 1 | 1 | 2 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [siamese_fixed] | 0.6038 | 0.1052 | 0.0000 | 0.4985 | 0.5831 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 8 | 2 | 2 | 14 |

## p* distribution

median 34, max 60, hits p_max_abs=60: 2/16

## Timing

clustering total 1.01 min (60.8 s, 3.80 s/recording, max 10.8 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.938 [-1.000, -0.812] | +2.875 [+2.250, +3.562] | 0.000352 |
| nmesc_ecapa | 0.5625 | 0.4375 | -0.562 [-0.812, -0.312] | +2.500 [+2.000, +3.062] | 0.000352 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| TS3003c | 4 | 10 | 18 14 12 11 10 10 9 8 6 4 | 1.23 | 48 |
| TS3003d | 4 | 10 | 25 14 12 11 10 8 7 6 4 3 | 1.09 | 48 |
| EN2002a | 4 | 1 | 100 | 1.49 | 25 |
| EN2002d | 4 | 1 | 100 | 1.03 | 42 |
| ES2004a | 4 | 1 | 100 | 1.22 | 28 |

## Per-recording predictions

See `predictions.csv`.
