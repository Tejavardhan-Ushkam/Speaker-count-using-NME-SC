# nmesc_ecapa — ami / dev

git commit `b44d128e6bd941225b19dfc1325b34673610b387-dirty`; resolved config in `config_resolved.yaml`.

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
| 18 | 0.6667 | 0.9444 | 0.3889 | +0.389 | 0.6667 | 0.0972 | 0.0000 |

Bootstrap 95 % CI: MAE [0.111, 0.667], exact [0.444, 0.889].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.667 | 0.944 | 0.389 | 0.389 | 0.667 | 0.097 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 | 5 | 6 |
|---|---|---|---|
| 4 | 12 | 5 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa | 0.1276 | 0.1065 | 0.0000 | 0.0211 | 0.0556 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 5 | 0 | 0 | 0 | 2 |

## p* distribution

median 4, max 14, hits p_max_abs=60: 0/18

## Timing

clustering total 1.02 min (61.2 s, 3.40 s/recording, max 10.9 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.333 [-0.556, -0.111] | +0.389 [+0.111, +0.667] | 0.0196 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011d | 4 | 6 | 36 24 18 10 9 3 | 2.41 | 3 |
| ES2011c | 4 | 5 | 33 25 22 19 1 | 1.76 | 3 |
| IB4001 | 4 | 5 | 54 32 9 5 1 | 2.69 | 4 |
| IS1008c | 4 | 5 | 38 28 17 15 1 | 1.21 | 4 |
| TS3004a | 4 | 5 | 51 23 14 11 1 | 3.04 | 5 |

## Per-recording predictions

See `predictions.csv`.
