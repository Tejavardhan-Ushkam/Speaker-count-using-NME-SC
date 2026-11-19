# snet_affnet_pp [ami_trained] — voxconverse / test_pyannote

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
| vad.source | pyannote |
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
| 232 | 0.2931 | 0.5302 | 2.9267 | +0.142 | 0.3966 | 0.8832 | 0.2500 |

Bootstrap 95 % CI: MAE [2.345, 3.560], exact [0.237, 0.353].

## Per-K-bin breakdown

| bin | n | exact | within1 | mae | signed | rel_acc | rel_err_mean | rel_err_median |
|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0.467 | 0.667 | 5.933 | 5.933 | 0.467 | 5.933 | 1.000 |
| 2 | 31 | 0.516 | 0.774 | 2.129 | 2.000 | 0.516 | 1.065 | 0.000 |
| 3 | 18 | 0.278 | 0.667 | 4.222 | 3.556 | 0.278 | 1.407 | 0.333 |
| 4 | 22 | 0.364 | 0.636 | 2.136 | 0.955 | 0.364 | 0.534 | 0.250 |
| 5-7 | 63 | 0.286 | 0.571 | 2.032 | -0.063 | 0.413 | 0.331 | 0.167 |
| 8-12 | 65 | 0.154 | 0.338 | 2.815 | -1.831 | 0.338 | 0.294 | 0.250 |
| 13+ | 18 | 0.222 | 0.278 | 5.000 | -4.444 | 0.444 | 0.325 | 0.212 |

## Confusion (rows K, columns K^)

| K | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 18 | 20 | 21 | 22 | 24 | 25 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 7 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 |
| 2 | 2 | 16 | 6 | 1 | 3 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 |
| 3 | 1 | 4 | 5 | 3 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 |
| 4 | 0 | 4 | 5 | 8 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 5 | 0 | 1 | 3 | 2 | 3 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| 6 | 0 | 2 | 0 | 5 | 1 | 5 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 7 | 0 | 3 | 2 | 1 | 2 | 6 | 10 | 2 | 2 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 |
| 8 | 0 | 2 | 0 | 1 | 3 | 4 | 3 | 6 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 9 | 0 | 0 | 3 | 1 | 0 | 0 | 2 | 1 | 3 | 2 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 10 | 0 | 0 | 1 | 0 | 0 | 2 | 1 | 1 | 1 | 1 | 2 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 11 | 1 | 0 | 1 | 0 | 1 | 2 | 2 | 0 | 4 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 13 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 14 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| 15 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 17 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 18 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 19 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| 21 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |

## DER (collar ±0.25 s)

| | mean DER | miss | FA | confusion | DER, overlap skipped |
|---|---|---|---|---|---|
| snet_affnet_pp [ami_trained] | 0.2121 | 0.0672 | 0.0088 | 0.1361 | 0.1948 |

## Cluster health (number of recordings)

| smallest<3% | largest>80% | K^=k_max | eigengap K=k_max | gap_ratio<1.5 |
|---|---|---|---|---|
| 91 | 27 | 5 | 5 | 53 |

## p* distribution

median 6, max 60, hits p_max_abs=60: 3/232

## Timing

clustering total 11.77 min (706.0 s, 3.04 s/recording, max 8.1 s)

## SpectralNet v2 self-check

K^ agreement with exact eigh: **0.983** (228/232); Ritz-value max rel. error (first k_max+1, excluding λ1): median 2.56e-01, max 5.05e+03 (dominated by near-zero within-cluster eigenvalues); max |Δλ| / λ_(k_max+1): median 0.004, max 0.732.

## 5 worst recordings

| rec | K | K^ | cluster sizes % | gap_ratio | p* |
|---|---|---|---|---|---|
| euqef | 1 | 25 | 7 7 7 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 4 | 1.67 | 1 |
| dohag | 1 | 24 | 7 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 2 2 2 2 2 2 2 | 1.02 | 1 |
| wdvva | 2 | 25 | 7 5 5 5 5 5 5 4 4 4 4 4 4 4 4 4 4 3 3 3 3 3 3 3 3 | 1.13 | 1 |
| fuzfh | 3 | 25 | 7 7 7 7 7 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 3 | 2.23 | 1 |
| msbyq | 4 | 25 | 7 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 5 2 2 2 2 2 2 2 | 2.15 | 2 |

## Per-recording predictions

See `predictions.csv`.
