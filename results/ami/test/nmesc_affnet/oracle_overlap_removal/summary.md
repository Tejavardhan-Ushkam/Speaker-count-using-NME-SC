# nmesc_affnet [oracle_overlap_removal] — ami / test

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
| affinity.oracle_overlap_removal (ORACLE) | True |
| postprocess.enabled | False |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.8750 | 0.9375 | 0.3750 | +0.250 | 0.8750 | 0.0938 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 1.062], exact [0.688, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.867 | 0.933 | 0.400 | 0.267 | 0.867 | 0.100 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 9 |
|---|---|---|---|
| 3 | 1 | 0 | 0 |
| 4 | 1 | 13 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [oracle_overlap_removal] | 0.1528 | 0.1052 | 0.0000 | 0.0476 | 0.0700 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 2 | 1 | 0 | 0 | 2 |

## p* distribution

median 4, max 16, hits p_max_abs=60: 0/16

## Timing

clustering total 0.37 min (22.5 s, 1.40 s/recording, max 2.5 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.062 [-0.250, +0.125] | +0.312 [-0.125, +1.000] | 0.414 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.312 [+0.000, +0.625] | -0.062 [-0.625, +0.750] | 0.248 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| IS1009a | 4 | 9 | 33 27 15 7 5 5 3 3 3 | 1.41 | 5 |
| TS3003a | 4 | 3 | 93 5 2 | 1.55 | 4 |
| EN2002a | 4 | 4 | 46 22 19 13 | 4.10 | 5 |
| EN2002b | 4 | 4 | 52 21 15 12 | 1.97 | 3 |
| EN2002c | 3 | 3 | 37 33 30 | 7.22 | 5 |

## Per-recording predictions

See `predictions.csv`.
