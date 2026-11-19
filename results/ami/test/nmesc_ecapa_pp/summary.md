# nmesc_ecapa_pp — ami / test

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
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | True |
| postprocess.min_cluster_share (used) | 0.02 |
| postprocess.merge_threshold (used) | 0.6 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.source (used) | results/tuning/nmesc_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.7500 | 1.0000 | 0.2500 | +0.125 | 0.7500 | 0.0625 | 0.0000 |

Bootstrap 95 % CI: MAE [0.062, 0.500], exact [0.500, 0.938].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.733 | 1.000 | 0.267 | 0.133 | 0.733 | 0.067 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 | 5 |
|---|---|---|---|
| 3 | 1 | 0 | 0 |
| 4 | 1 | 11 | 3 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa_pp | 0.1261 | 0.1052 | 0.0000 | 0.0209 | 0.0423 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 2 | 1 | 0 | 0 | 2 |

## p* distribution

median 6, max 18, hits p_max_abs=60: 0/16

## Timing

clustering total 1.31 min (78.8 s, 4.93 s/recording, max 17.7 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.188 [-0.438, +0.062] | +0.188 [-0.062, +0.438] | 0.18 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.188 [-0.062, +0.438] | -0.188 [-0.438, +0.062] | 0.18 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| EN2002a | 4 | 5 | 39 21 18 17 5 | 1.36 | 5 |
| EN2002d | 4 | 5 | 33 25 24 11 6 | 1.65 | 4 |
| TS3003a | 4 | 3 | 90 7 2 | 1.25 | 5 |
| TS3003d | 4 | 5 | 57 16 13 12 2 | 4.18 | 5 |
| EN2002b | 4 | 4 | 43 25 20 13 | 1.82 | 4 |

## Per-recording predictions

See `predictions.csv`.
