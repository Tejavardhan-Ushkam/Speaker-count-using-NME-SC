# nmesc_ecapa_pp [vox_tuned] — ami / test

git commit `3d875af9e0076f603863f592ff6fcc5a8b8d0801`; resolved config in `config_resolved.yaml`.

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
| postprocess.min_cluster_share (used) | 0.03 |
| postprocess.merge_threshold (used) | 0.7 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.share_mode (used) | absolute |
| postprocess.p_min (used) | 4 |
| postprocess.source (used) | results/tuning_vox/nmesc_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.8125 | 0.9375 | 0.2500 | +0.000 | 0.8125 | 0.0625 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.562], exact [0.625, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.800 | 0.933 | 0.267 | 0.000 | 0.800 | 0.067 | 0.000 |

## Confusion (rows K, columns K^)

| K | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| 3 | 0 | 1 | 0 | 0 |
| 4 | 1 | 0 | 12 | 2 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa_pp [vox_tuned] | 0.1243 | 0.1052 | 0.0000 | 0.0191 | 0.0403 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 1 | 0 | 0 | 3 |

## p* distribution

median 5, max 8, hits p_max_abs=60: 0/16

## Timing

clustering total 0.95 min (56.8 s, 3.55 s/recording, max 11.6 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 0.9375 | 0.0625 | -0.125 [-0.375, +0.125] | +0.188 [-0.125, +0.500] | 0.257 |
| nmesc_ecapa | 0.5625 | 0.4375 | +0.250 [+0.000, +0.500] | -0.188 [-0.500, +0.188] | 0.317 |

n = 16 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| TS3003a | 4 | 2 | 92 8 | 1.25 | 5 |
| EN2002a | 4 | 5 | 39 21 18 17 5 | 1.36 | 5 |
| EN2002d | 4 | 5 | 33 25 24 11 6 | 1.65 | 4 |
| EN2002b | 4 | 4 | 43 25 20 13 | 1.82 | 4 |
| EN2002c | 3 | 3 | 40 31 29 | 2.33 | 6 |

## Per-recording predictions

See `predictions.csv`.
