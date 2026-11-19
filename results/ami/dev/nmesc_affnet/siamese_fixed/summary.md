# nmesc_affnet [siamese_fixed] — ami / dev

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
| 18 | 0.0000 | 0.0000 | 3.2222 | -1.778 | 0.0000 | 0.8056 | 0.7500 |

Bootstrap 95 % CI: MAE [3.000, 3.556], exact [0.000, 0.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.000 | 0.000 | 3.222 | -1.778 | 0.000 | 0.806 | 0.750 |

## Confusion (rows K, columns K^)

| K | 1 | 7 | 9 |
|---|---|---|---|
| 4 | 15 | 1 | 2 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [siamese_fixed] | 0.6479 | 0.1065 | 0.0000 | 0.5414 | 0.6392 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 15 | 0 | 0 | 12 |

## p* distribution

median 34, max 60, hits p_max_abs=60: 2/18

## Timing

clustering total 0.95 min (57.2 s, 3.18 s/recording, max 9.3 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -1.000 [-1.000, -1.000] | +3.222 [+3.000, +3.556] | 4.78e-05 |
| nmesc_ecapa | 0.6667 | 0.3889 | -0.667 [-0.889, -0.444] | +2.833 [+2.444, +3.222] | 0.000128 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| IB4001 | 4 | 9 | 19 15 11 10 10 9 9 9 7 | 1.34 | 57 |
| IB4010 | 4 | 9 | 20 16 15 14 10 9 6 5 4 | 1.07 | 60 |
| ES2011a | 4 | 1 | 100 | 1.45 | 6 |
| ES2011b | 4 | 1 | 100 | 1.64 | 9 |
| ES2011c | 4 | 1 | 100 | 1.79 | 12 |

## Per-recording predictions

See `predictions.csv`.
