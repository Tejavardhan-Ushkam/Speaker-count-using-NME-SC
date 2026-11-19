# nmesc_affnet [no_time] — ami / dev

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
| 18 | 0.8889 | 0.9444 | 0.1667 | +0.056 | 0.8889 | 0.0417 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.444], exact [0.722, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.889 | 0.944 | 0.167 | 0.056 | 0.889 | 0.042 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 6 |
|---|---|---|---|
| 4 | 1 | 16 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [no_time] | 0.1309 | 0.1065 | 0.0000 | 0.0244 | 0.0582 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 2 |

## p* distribution

median 4, max 9, hits p_max_abs=60: 0/18

## Timing

clustering total 0.78 min (46.8 s, 2.60 s/recording, max 8.2 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.111 [-0.278, +0.000] | +0.167 [+0.000, +0.444] | 0.18 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.222 [+0.000, +0.444] | -0.222 [-0.444, +0.000] | 0.102 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011d | 4 | 6 | 36 24 18 10 8 4 | 1.57 | 3 |
| ES2011a | 4 | 3 | 49 29 22 | 2.23 | 3 |
| ES2011b | 4 | 4 | 28 27 27 18 | 9.33 | 7 |
| ES2011c | 4 | 4 | 34 25 23 19 | 5.84 | 4 |
| IB4001 | 4 | 4 | 54 32 9 5 | 4.60 | 3 |

## Per-recording predictions

See `predictions.csv`.
