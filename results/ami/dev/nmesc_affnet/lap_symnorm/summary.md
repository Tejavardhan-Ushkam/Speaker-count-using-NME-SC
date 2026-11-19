# nmesc_affnet [lap_symnorm] — ami / dev

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
| 18 | 0.8889 | 0.8889 | 0.4444 | +0.444 | 0.8889 | 0.1111 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 1.111], exact [0.722, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.889 | 0.889 | 0.444 | 0.444 | 0.889 | 0.111 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 | 7 | 9 |
|---|---|---|---|
| 4 | 16 | 1 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [lap_symnorm] | 0.1484 | 0.1065 | 0.0000 | 0.0420 | 0.0770 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 4 |

## p* distribution

median 6, max 14, hits p_max_abs=60: 0/18

## Timing

clustering total 1.30 min (78.3 s, 4.35 s/recording, max 18.6 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.111 [-0.278, +0.000] | +0.444 [+0.000, +1.111] | 0.18 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.222 [+0.000, +0.444] | +0.056 [-0.444, +0.722] | 0.527 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011a | 4 | 9 | 31 27 14 12 7 5 2 1 1 | 1.06 | 5 |
| ES2011d | 4 | 7 | 24 20 18 16 10 8 4 | 1.20 | 10 |
| ES2011b | 4 | 4 | 29 27 26 18 | 5.42 | 5 |
| ES2011c | 4 | 4 | 35 25 22 19 | 3.60 | 4 |
| IB4001 | 4 | 4 | 54 33 8 4 | 1.23 | 5 |

## Per-recording predictions

See `predictions.csv`.
