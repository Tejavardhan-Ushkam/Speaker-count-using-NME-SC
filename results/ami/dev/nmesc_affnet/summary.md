# nmesc_affnet — ami / dev

git commit `03c397639fc8b46421e4beac89184e5b41eafc30-dirty`; resolved config in `config_resolved.yaml`.

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
| 18 | 1.0000 | 1.0000 | 0.0000 | +0.000 | 1.0000 | 0.0000 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.000], exact [1.000, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 |
|---|---|
| 4 | 18 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet | 0.1234 | 0.1065 | 0.0000 | 0.0170 | 0.0506 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 3 |

## p* distribution

median 4, max 9, hits p_max_abs=60: 0/18

## Timing

clustering total 1.09 min (65.5 s, 3.64 s/recording, max 9.8 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | 1 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.333 [+0.111, +0.556] | -0.389 [-0.667, -0.111] | 0.0196 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011a | 4 | 4 | 51 27 22 1 | 1.62 | 3 |
| ES2011b | 4 | 4 | 28 27 26 18 | 7.41 | 4 |
| ES2011c | 4 | 4 | 35 25 22 19 | 6.50 | 4 |
| ES2011d | 4 | 4 | 36 28 19 17 | 1.45 | 6 |
| IB4001 | 4 | 4 | 54 33 9 4 | 1.43 | 5 |

## Per-recording predictions

See `predictions.csv`.
