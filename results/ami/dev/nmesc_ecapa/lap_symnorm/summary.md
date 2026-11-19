# nmesc_ecapa [lap_symnorm] — ami / dev

git commit `ee0f80eb04050f8bcecfe88f09242757a5741e9b-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
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
| 18 | 0.6111 | 0.9444 | 0.4444 | +0.444 | 0.6111 | 0.1111 | 0.0000 |

Bootstrap 95 % CI: MAE [0.167, 0.722], exact [0.389, 0.833].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.611 | 0.944 | 0.444 | 0.444 | 0.611 | 0.111 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 | 5 | 6 |
|---|---|---|---|
| 4 | 11 | 6 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa [lap_symnorm] | 0.1278 | 0.1065 | 0.0000 | 0.0214 | 0.0556 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 8 | 0 | 0 | 0 | 1 |

## p* distribution

median 6, max 13, hits p_max_abs=60: 0/18

## Timing

clustering total 1.27 min (76.2 s, 4.23 s/recording, max 12.6 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.389 [-0.611, -0.167] | +0.444 [+0.167, +0.722] | 0.0114 |
| nmesc_ecapa | 0.6667 | 0.3889 | -0.056 [-0.167, +0.000] | +0.056 [+0.000, +0.167] | 0.317 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011d | 4 | 6 | 37 25 18 9 9 2 | 3.08 | 8 |
| ES2011c | 4 | 5 | 34 25 22 19 1 | 2.20 | 5 |
| IB4001 | 4 | 5 | 54 32 9 5 1 | 3.91 | 6 |
| IB4002 | 4 | 5 | 40 32 16 10 2 | 1.18 | 8 |
| IS1008c | 4 | 5 | 39 28 17 15 1 | 1.58 | 5 |

## Per-recording predictions

See `predictions.csv`.
