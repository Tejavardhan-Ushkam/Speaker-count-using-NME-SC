# nmesc_ecapa — ami / test_pyannote

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
| vad.source | pyannote |
| affinity.refine | False |
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | False |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 16 | 0.6875 | 0.9375 | 0.3750 | +0.125 | 0.6875 | 0.0938 | 0.0000 |

Bootstrap 95 % CI: MAE [0.125, 0.688], exact [0.438, 0.875].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 1.000 | 1.000 | 0.000 | 0.000 | 1.000 | 0.000 | 0.000 |
| 4 | 15 | 0.667 | 0.933 | 0.400 | 0.133 | 0.667 | 0.100 | 0.000 |

## Confusion (rows K, columns K^)

| K | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| 3 | 0 | 1 | 0 | 0 |
| 4 | 1 | 0 | 10 | 4 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| nmesc_ecapa | 0.1687 | 0.1424 | 0.0124 | 0.0139 | 0.0903 |

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 3 | 1 | 0 | 0 | 3 |

## p* distribution

median 6, max 12, hits p_max_abs=60: 0/16

## Timing

clustering total 0.96 min (57.5 s, 3.59 s/recording, max 10.0 s)

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| TS3003a | 4 | 2 | 93 7 | 2.44 | 12 |
| EN2002b | 4 | 5 | 41 23 19 14 3 | 1.20 | 6 |
| EN2002d | 4 | 5 | 33 25 25 10 7 | 1.27 | 5 |
| TS3003c | 4 | 5 | 37 27 23 12 1 | 2.07 | 5 |
| TS3003d | 4 | 5 | 56 17 14 13 1 | 2.06 | 6 |

## Per-recording predictions

See `predictions.csv`.
