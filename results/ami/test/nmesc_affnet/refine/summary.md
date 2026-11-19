# nmesc_affnet [refine] — ami / test

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
| 16 | 0.6875 | 0.7500 | 0.7500 | +0.750 | 0.6875 | 0.1875 | 0.0000 |

Bootstrap 95 % CI: MAE [0.188, 1.375], exact [0.438, 0.875].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.667 | 0.733 | 0.800 | 0.800 | 0.667 | 0.200 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|
| 3 | 1 | 0 | 0 | 0 | 0 | 0 |
| 4 | 0 | 10 | 1 | 2 | 1 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [refine] | 0.2269 | 0.1052 | 0.0000 | 0.1217 | 0.1493 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 2 | 0 | 0 | 0 | 3 |

## p* distribution

median 59, max 60, hits p_max_abs=60: 8/16  **(often at the cap: raise p_max_abs)**

## Timing

clustering total 0.50 min (30.2 s, 1.89 s/recording, max 5.1 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.250 [-0.500, +0.000] | +0.688 [+0.125, +1.375] | 0.0578 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.125 [-0.250, +0.500] | +0.312 [-0.375, +1.000] | 0.41 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2004a | 4 | 8 | 16 15 15 14 13 11 10 5 | 1.69 | 40 |
| IS1009a | 4 | 7 | 33 28 17 10 6 3 2 | 2.60 | 7 |
| IS1009c | 4 | 6 | 24 21 16 15 13 11 | 1.67 | 6 |
| IS1009d | 4 | 6 | 28 22 18 15 10 7 | 2.13 | 14 |
| ES2004c | 4 | 5 | 38 20 16 13 12 | 2.76 | 25 |

## Per-recording predictions

See `predictions.csv`.
