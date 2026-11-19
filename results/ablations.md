AMI only (VoxConverse unavailable, so the "training corpora" ablation is not run). Each variant differs from its default in one setting; AffinityNet variants were retrained and selected on AMI dev exactly like the default. No post-processing in these rows unless the method name says `_pp`.

| ablation | variant | dev exact | dev MAE | test exact | test MAE | test DER |
|---|---|---|---|---|---|---|
| Laplacian | unnormalized (default) | 0.667 | 0.389 | 0.562 | 0.438 | 0.127 |
|  | sym_norm | 0.611 | 0.444 | 0.500 | 0.500 | 0.128 |
|  | unnormalized (default), AffinityNet | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | sym_norm, AffinityNet | 0.889 | 0.444 | 0.812 | 0.375 | 0.148 |
| AffinityNet context | 4-layer Transformer (default) | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | 0 layers (per-segment residual MLP) | 0.944 | 0.056 | 0.812 | 0.312 | 0.131 |
| Time encoding | on (default) | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | off | 0.889 | 0.167 | 1.000 | 0.000 | 0.129 |
| Speaker-dropout augmentation | on (default) | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | off | 0.944 | 0.056 | 0.750 | 0.250 | 0.149 |
| Loss | BCE + SupCon (default) | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | BCE only | 0.889 | 0.167 | 0.875 | 0.125 | 0.127 |
| Overlap handling (training labels) | clean-only loss (default) | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | most-overlap labels (old project) | 0.833 | 0.222 | 0.875 | 0.125 | 0.125 |
| Oracle overlap removal (ORACLE, upper bound) | off, raw ECAPA | 0.667 | 0.389 | 0.562 | 0.438 | 0.127 |
|  | on, raw ECAPA | 0.722 | 0.333 | 0.750 | 0.250 | 0.123 |
|  | off, AffinityNet | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | on, AffinityNet | 0.889 | 0.222 | 0.875 | 0.375 | 0.153 |
| Refinement ops (Wang et al. 2018) | off, raw ECAPA | 0.667 | 0.389 | 0.562 | 0.438 | 0.127 |
|  | on, raw ECAPA | 0.944 | 0.056 | 0.812 | 0.250 | 0.125 |
|  | off, AffinityNet | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |
|  | on, AffinityNet | 0.722 | 0.556 | 0.688 | 0.750 | 0.227 |
| SpectralNet warm start | on (default) | 1.000 | 0.000 | 0.812 | 0.500 | 0.160 |
|  | off | 1.000 | 0.000 | 0.812 | 0.500 | 0.161 |
| VAD | oracle, nmesc_ecapa | 0.667 | 0.389 | 0.562 | 0.438 | 0.127 |
|  | pyannote, nmesc_ecapa | – | – | 0.688 | 0.375 | 0.169 |
|  | oracle, snet_affnet_pp | 1.000 | 0.000 | 0.812 | 0.500 | 0.160 |
|  | pyannote, snet_affnet_pp | – | – | 0.750 | 0.438 | 0.199 |
| Old Siamese, flaws 1-2 fixed only | raw ECAPA (nmesc_ecapa) | 0.667 | 0.389 | 0.562 | 0.438 | 0.127 |
|  | Siamese (no output ReLU, cosine loss) | 0.000 | 3.222 | 0.000 | 2.938 | 0.604 |
|  | AffinityNet (nmesc_affnet) | 1.000 | 0.000 | 0.812 | 0.500 | 0.150 |

SpectralNet warm start, mean clustering time per AMI test recording — on: 14.4 s/recording; off: 14.8 s/recording.
