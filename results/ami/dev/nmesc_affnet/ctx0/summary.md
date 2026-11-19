# nmesc_affnet [ctx0] — ami / dev

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
| 18 | 0.9444 | 1.0000 | 0.0556 | -0.056 | 0.9444 | 0.0139 | 0.0000 |

Bootstrap 95 % CI: MAE [0.000, 0.167], exact [0.833, 1.000].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 4 | 18 | 0.944 | 1.000 | 0.056 | -0.056 | 0.944 | 0.014 | 0.000 |

## Confusion (rows K, columns K^)

| K | 3 | 4 |
|---|---|---|
| 4 | 1 | 17 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_affnet [ctx0] | 0.1236 | 0.1065 | 0.0000 | 0.0171 | 0.0507 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 1 |

## p* distribution

median 4, max 11, hits p_max_abs=60: 0/18

## Timing

clustering total 1.32 min (79.1 s, 4.40 s/recording, max 12.9 s)

## Against the baselines (paired; differences = this run − baseline)

| baseline | baseline exact | baseline MAE | Δ exact [95 % CI] | Δ MAE [95 % CI] | Wilcoxon p (|K^−K|) |
|---|---|---|---|---|---|
| baseline_mode | 1.0000 | 0.0000 | -0.056 [-0.167, +0.000] | +0.056 [+0.000, +0.167] | 0.317 |
| nmesc_ecapa | 0.6667 | 0.3889 | +0.278 [+0.000, +0.500] | -0.333 [-0.611, -0.056] | 0.0578 |

n = 18 recordings: statistical power is low.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| ES2011a | 4 | 3 | 50 26 24 | 1.95 | 11 |
| ES2011b | 4 | 4 | 28 27 27 18 | 4.91 | 4 |
| ES2011c | 4 | 4 | 33 26 23 18 | 2.84 | 4 |
| ES2011d | 4 | 4 | 40 24 18 17 | 1.24 | 5 |
| IB4001 | 4 | 4 | 54 33 8 5 | 1.81 | 3 |

## Per-recording predictions

See `predictions.csv`.
