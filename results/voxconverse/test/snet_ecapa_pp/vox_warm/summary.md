# snet_ecapa_pp [vox_warm] — voxconverse / test

git commit `582a65b989a5ea57512b7456ad0b40386e6260ac`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | ecapa |
| clustering.backend | spectralnet |
| clustering.laplacian | unnormalized |
| clustering.k_max | 25 |
| clustering.p_max_abs | 60 |
| clustering.coarse_to_fine | True |
| clustering.eig_solver | sparse |
| vad.source | oracle |
| affinity.refine | False |
| affinity.oracle_overlap_removal (ORACLE) | False |
| postprocess.enabled | True |
| postprocess.min_cluster_share (used) | 0.15 |
| postprocess.merge_threshold (used) | 0.7 |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.share_mode (used) | relative |
| postprocess.p_min (used) | 4 |
| postprocess.source (used) | results/tuning_vox_warm/snet_ecapa_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 232 | 0.3793 | 0.6121 | 1.8621 | -1.776 | 0.4871 | 0.2418 | 0.1667 |

Bootstrap 95 % CI: MAE [1.569, 2.160], exact [0.319, 0.444].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.867 | 1.000 | 0.133 | 0.133 | 0.867 | 0.133 | 0.000 |
| 2 | 31 | 0.903 | 1.000 | 0.097 | -0.032 | 0.903 | 0.048 | 0.000 |
| 3 | 18 | 0.444 | 0.778 | 0.778 | -0.667 | 0.444 | 0.259 | 0.333 |
| 4 | 22 | 0.364 | 0.818 | 0.864 | -0.682 | 0.364 | 0.216 | 0.250 |
| 5-7 | 63 | 0.349 | 0.603 | 1.556 | -1.460 | 0.476 | 0.244 | 0.167 |
| 8-12 | 65 | 0.108 | 0.323 | 3.154 | -3.154 | 0.323 | 0.332 | 0.333 |
| 13+ | 18 | 0.111 | 0.278 | 5.056 | -4.944 | 0.278 | 0.345 | 0.400 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 13 | 15 | 16 | 18 | 21 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 2 | 2 | 28 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 3 | 4 | 5 | 8 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 4 | 1 | 3 | 8 | 8 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 5 | 0 | 1 | 2 | 5 | 4 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 6 | 0 | 2 | 3 | 2 | 3 | 8 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 1 | 3 | 4 | 3 | 3 | 7 | 10 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 8 | 1 | 0 | 1 | 4 | 5 | 2 | 6 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 | 0 | 1 | 4 | 2 | 0 | 3 | 0 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 10 | 1 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 3 | 2 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11 | 0 | 0 | 1 | 1 | 3 | 1 | 2 | 0 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 12 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| 13 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| 15 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 1 | 1 | 0 | 0 |
| 17 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_ecapa_pp [vox_warm] | 0.0766 | 0.0434 | 0.0000 | 0.0331 | 0.0571 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 48 | 41 | 0 | 0 | 26 |

## p* distribution

median 5, max 55, hits p_max_abs=60: 0/232

## Timing

clustering total 15.04 min (902.2 s, 3.89 s/recording, max 12.3 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **0.987** (229/232); Ritz-value max rel. error (first k_max+1, excluding λ1): median 8.76e+00, max 6.70e+04 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.054, max 0.431.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| eqsta | 15 | 4 | 50 42 5 3 | 1.99 | 6 |
| pwnsw | 13 | 2 | 74 26 | 1.88 | 7 |
| jeymh | 18 | 8 | 27 22 18 16 11 2 2 2 | 2.17 | 4 |
| qajyo | 17 | 7 | 46 18 10 9 9 4 4 | 2.30 | 9 |
| cwbvu | 10 | 1 | 100 | 5.74 | 35 |

## Per-recording predictions

See `predictions.csv`.
