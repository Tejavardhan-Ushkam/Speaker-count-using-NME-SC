# nmesc_affnet [refine] — ami / dev

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
| affinity.refine | True |
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | False |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 18 | 0.7222 | 0.8333 | 0.5556 | +0.556 | 0.7222 | 0.1389 | 0.0000 |

Bootstrap 95 % CI: MAE [0.167, 1.056], exact [0.500, 0.889].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.722 | 0.833 | 0.556 | 0.556 | 0.722 | 0.139 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| 4 | 13 | 2 | 1 | 2 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [refine] | 0.1874 | 0.1065 | 0.0000 | 0.0809 | 0.1185 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 6 |

## p* distribution

median 60, max 60, hits p_max_abs=60: 9/18  **(often at the cap: raise p_max_abs)**

## Timing

clustering total 0.56 min (33.4 s, 1.86 s/recording, max 4.2 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.278 [-0.500, -0.111] | +0.556 [+0.167, +1.056] | 0.0412 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.056 [-0.222, +0.333] | +0.167 [-0.333, +0.667] | 0.465 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| IB4001 | 4 | 7 | 35 26 11 9 9 7 3 | 2.12 | 25 |
| TS3004a | 4 | 7 | 29 17 14 13 11 9 7 | 1.10 | 41 |
| IS1008a | 4 | 6 | 40 19 17 11 8 6 | 1.96 | 10 |
| ES2011a | 4 | 5 | 25 25 21 16 14 | 1.62 | 50 |
| IS1008d | 4 | 5 | 26 24 22 15 12 | 1.16 | 59 |

## Per-recording predictions

See `predictions.csv`.
