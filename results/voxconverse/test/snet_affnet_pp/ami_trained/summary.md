# snet_affnet_pp [ami_trained] — voxconverse / test

git commit `f6536655b6e360d377ecb73f941907b2c81816a7-dirty`; resolved config in `config_resolved.yaml`.

## Configuration

| key | value |
|---|---|
| affinity.source | affnet |
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
| postprocess.min_cluster_share (used) | 0.0 |
| postprocess.merge_threshold (used) | None |
| postprocess.single_speaker_threshold (used) | None |
| postprocess.source (used) | results/tuning_ami_only/snet_affnet_pp/best.yaml |

## Counting accuracy

| n | exact | ±1 | MAE | mean signed error | rel. acc (τ=0.15) | mean rel. err | median rel. err |
|---|---|---|---|---|---|---|---|
| 232 | 0.2931 | 0.5733 | 2.7845 | +0.371 | 0.4310 | 0.8590 | 0.2111 |

Bootstrap 95 % CI: MAE [2.207, 3.418], exact [0.237, 0.353].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.533 | 0.600 | 5.733 | 5.733 | 0.533 | 5.733 | 0.000 |
| 2 | 31 | 0.613 | 0.806 | 2.000 | 1.871 | 0.613 | 1.000 | 0.000 |
| 3 | 18 | 0.278 | 0.667 | 4.167 | 3.500 | 0.278 | 1.389 | 0.333 |
| 4 | 22 | 0.364 | 0.682 | 2.318 | 1.318 | 0.364 | 0.580 | 0.250 |
| 5-7 | 63 | 0.270 | 0.635 | 2.159 | 0.317 | 0.413 | 0.357 | 0.167 |
| 8-12 | 65 | 0.138 | 0.415 | 2.462 | -1.662 | 0.415 | 0.259 | 0.250 |
| 13+ | 18 | 0.111 | 0.278 | 4.222 | -3.444 | 0.389 | 0.289 | 0.282 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 20 | 21 | 22 | 23 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 8 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 0 |
| 2 | 2 | 19 | 4 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| 3 | 1 | 4 | 5 | 3 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 |
| 4 | 0 | 3 | 5 | 8 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 |
| 5 | 0 | 1 | 0 | 4 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 |
| 6 | 0 | 1 | 0 | 2 | 3 | 7 | 4 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 0 | 2 | 1 | 3 | 5 | 7 | 7 | 2 | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |
| 8 | 0 | 0 | 0 | 2 | 4 | 5 | 3 | 4 | 1 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 | 0 | 0 | 3 | 1 | 0 | 0 | 3 | 2 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 10 | 0 | 1 | 0 | 0 | 0 | 2 | 0 | 0 | 1 | 2 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11 | 0 | 0 | 1 | 0 | 0 | 3 | 1 | 2 | 1 | 1 | 0 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 13 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 15 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 17 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_affnet_pp [ami_trained] | 0.1856 | 0.0434 | 0.0000 | 0.1422 | 0.1683 |

With oracle VAD the missed-speech part of DER comes only from overlapped speech (one label per frame), and false alarm is ~0.

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 93 | 27 | 3 | 3 | 40 |

## p* distribution

median 6, max 56, hits p_max_abs=60: 0/232

## Timing

clustering total 11.62 min (696.9 s, 3.00 s/recording, max 9.5 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **0.991** (230/232); Ritz-value max rel. error (first k_max+1, excluding λ1): median 4.98e-01, max 7.93e+03 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.004, max 0.684.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| euqef | 1 | 24 | 7 7 7 7 7 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 | 1.58 | 1 |
| lubpm | 2 | 25 | 5 5 5 5 5 5 5 5 5 5 5 3 3 3 3 3 3 3 3 3 3 3 3 3 3 | 1.12 | 1 |
| neiye | 1 | 24 | 7 5 5 5 5 5 5 5 5 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 | 1.20 | 1 |
| wdvva | 2 | 25 | 12 8 7 5 5 4 4 4 4 4 4 3 3 3 3 3 3 3 3 3 3 3 3 3 3 | 2016.00 | 1 |
| dohag | 1 | 22 | 6 6 6 6 6 6 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 2 | 1.24 | 1 |

## Per-recording predictions

See `predictions.csv`.
