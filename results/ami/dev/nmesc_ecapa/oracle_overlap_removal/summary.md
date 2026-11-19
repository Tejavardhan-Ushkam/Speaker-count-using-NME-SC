# nmesc_ecapa [oracle_overlap_removal] — ami / dev

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
| 18 | 0.7222 | 0.9444 | 0.3333 | +0.333 | 0.7222 | 0.0833 | 0.0000 |

Bootstrap 95 % CI: MAE [0.111, 0.611], exact [0.500, 0.889].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.722 | 0.944 | 0.333 | 0.333 | 0.722 | 0.083 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 | 5 | 6 |
|---|---|---|---|
| 4 | 13 | 4 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa [oracle_overlap_removal] | 0.1288 | 0.1065 | 0.0000 | 0.0223 | 0.0561 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 4 | 0 | 0 | 0 | 1 |

## p* distribution

median 5, max 15, hits p_max_abs=60: 0/18

## Timing

clustering total 0.48 min (29.0 s, 1.61 s/recording, max 4.4 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.278 [-0.500, -0.111] | +0.333 [+0.111, +0.611] | 0.0339 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.056 [-0.111, +0.222] | -0.056 [-0.222, +0.111] | 0.564 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011d | 4 | 6 | 38 25 16 10 9 3 | 2.10 | 5 |
| ES2011c | 4 | 5 | 33 27 20 18 1 | 1.34 | 5 |
| IB4002 | 4 | 5 | 40 32 16 11 2 | 4.21 | 6 |
| TS3004a | 4 | 5 | 54 22 13 10 1 | 1.85 | 5 |
| TS3004d | 4 | 5 | 32 26 21 19 2 | 13.17 | 5 |

## Per-recording predictions

See `predictions.csv`.
