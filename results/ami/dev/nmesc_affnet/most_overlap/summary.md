# nmesc_affnet [most_overlap] — ami / dev

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
| 18 | 0.8333 | 0.9444 | 0.2222 | +0.111 | 0.8333 | 0.0556 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.500], exact [0.667, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.833 | 0.944 | 0.222 | 0.111 | 0.833 | 0.056 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 | 6 |
|---|---|---|---|---|
| 4 | 1 | 15 | 1 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [most_overlap] | 0.1264 | 0.1065 | 0.0000 | 0.0199 | 0.0540 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | 1 |

## p* distribution

median 5, max 10, hits p_max_abs=60: 0/18

## Timing

clustering total 1.00 min (60.0 s, 3.33 s/recording, max 10.6 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.167 [-0.333, +0.000] | +0.222 [+0.000, +0.500] | 0.102 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.167 [-0.056, +0.389] | -0.167 [-0.389, +0.056] | 0.18 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011d | 4 | 6 | 36 24 18 9 8 4 | 1.83 | 7 |
| ES2011a | 4 | 3 | 51 26 23 | 1.48 | 8 |
| TS3004d | 4 | 5 | 32 24 22 20 1 | 4.48 | 6 |
| ES2011b | 4 | 4 | 28 27 26 18 | 6.36 | 4 |
| ES2011c | 4 | 4 | 33 25 23 19 | 2.47 | 6 |

## Per-recording predictions

See `predictions.csv`.
