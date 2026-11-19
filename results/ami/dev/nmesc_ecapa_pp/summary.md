# nmesc_ecapa_pp — ami / dev

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
| 18 | 0.9444 | 1.0000 | 0.0556 | +0.056 | 0.9444 | 0.0139 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.167], exact [0.833, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.944 | 1.000 | 0.056 | 0.056 | 0.944 | 0.014 | 0.000 |

## Confusion (rows K, columns K^)

| K | 4 | 5 |
|---|---|---|
| 4 | 17 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa_pp | 0.1221 | 0.1065 | 0.0000 | 0.0156 | 0.0494 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 2 |

## p* distribution

median 4, max 14, hits p_max_abs=60: 0/18

## Timing

clustering total 1.02 min (61.2 s, 3.40 s/recording, max 10.9 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.056 [-0.167, +0.000] | +0.056 [+0.000, +0.167] | 0.317 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.278 [+0.111, +0.500] | -0.333 [-0.556, -0.111] | 0.0143 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011d | 4 | 5 | 36 24 18 18 3 | 2.41 | 3 |
| ES2011a | 4 | 4 | 47 27 23 3 | 3.64 | 14 |
| ES2011b | 4 | 4 | 28 27 27 18 | 6.21 | 4 |
| ES2011c | 4 | 4 | 34 25 23 19 | 1.76 | 3 |
| IB4001 | 4 | 4 | 54 32 9 5 | 2.69 | 4 |

## Per-recording predictions

See `predictions.csv`.
