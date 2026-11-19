# Speaker-count v2 — AffinityNet + SpectralNet v2

Estimates the number of speakers K per recording: ECAPA segment embeddings → (optional) AffinityNet,
a session-level Transformer that refines them → cosine affinity → fast NME-SC p* search → exact eigh or
SpectralNet v2 → eigengap K̂ → k-means labels → post-processing (prune tiny clusters, merge near-duplicates).

**Results:** [`results/SUMMARY.md`](results/SUMMARY.md) (tables, ablations, inferences, failure analysis, figures).
**Status:** trained/tuned on AMI only; VoxConverse test evaluated cross-corpus (`scripts/vox_crosscorpus.sh`, SUMMARY §1b). VoxConverse dev is still missing (Vox training/tuning steps are skipped automatically and picked up once
`dataset/voxconverse/{audio,rttm}/{dev,test}` exists). The build plan is [`prompt.md`](prompt.md).

## Environment

Locked set in `requirements.txt` (Python 3.10, torch 2.6.0+cu124, speechbrain 1.1.1, pyannote.audio 3.3.2). On this machine
the matching environment is the conda env `spectral`:

```bash
PY=/home/pm_students/miniconda3/envs/spectral/bin/python
```

Every GPU step falls back to CPU on out-of-memory (the GPU is shared), with the same results, only slower.
`pyannote/segmentation-3.0` is gated on Hugging Face (needs access via `HF_TOKEN` or a cached login).

## Layout

```
run.py                       single CLI
configs/base.yaml            all defaults (unknown --set keys raise an error)
configs/{ami,vox}_*.yaml     splits; configs/methods/*.yaml method presets; affnet_train.yaml
splits/                      VoxConverse 80/20 split (made by make-splits)
speakercount/                rttm, vad, segmentation, embedding, labels, pipeline, tune
  affinity/                  AffinityNet model/loss/data/train/infer; siamese.py (ablation)
  cluster/                   laplacian, nmesc (fast), spectralnet (v2), postprocess, kmeans, refine, run
  eval/                      metrics, der, stats, evaluate, report, compare, plots
tests/                       python tests/run_tests.py   (pytest-compatible; pytest is not installed)
scripts/run_all.sh           full pipeline; scripts/overnight.sh = Phase 5/6 + ablations (START_AT=N resumes)
work/ checkpoints/ results/  caches, models, outputs (results/<corpus>/<split>/<method>[/<tag>]/)
```

## Commands (times measured on AMI, RTX A5000 shared with another job)

| command | what | time |
|---|---|---|
| `$PY run.py check-data` | verify dataset, K histograms → `results/data_summary.md` | 30 s |
| `$PY run.py make-splits` | VoxConverse dev 80/20, stratified by K bin | seconds |
| `$PY run.py prepare --config configs/ami_train.yaml` | oracle VAD, 1.5 s/0.75 s segments, ECAPA, overlap labels (cached) | train 6 min, dev/test 45 s each |
| `$PY run.py train-affnet --config configs/affnet_train.yaml` | AffinityNet, early stopping on val | 12–30 min |
| `$PY run.py tune --method nmesc_ecapa_pp` | post-processing grid on val sets only | 1–2 min (SpectralNet: 4 min; first time +13 min pre-training) |
| `$PY run.py evaluate --config configs/ami_test.yaml --method snet_affnet_pp` | cluster + DER + predictions.csv + summary.md | 1–4 min |
| `$PY run.py report --config ... --method ...` | rewrite one run's summary.md | seconds |
| `$PY run.py compare` | `results/SUMMARY.md` | seconds |
| `$PY run.py plots` | `results/plots/*` (PNG + PDF) | 20 s |
| `$PY run.py inspect --config configs/ami_test.yaml --method snet_affnet_pp --recording EN2002a` | per-recording diagnostics | seconds |
| `bash scripts/run_all.sh` | everything, in order | ~1.5 h (AMI only) |

Every subcommand takes `--set dotted.key=value` (e.g. `--set clustering.laplacian=sym_norm --set method.tag=lap_symnorm`);
each run writes `config_resolved.yaml` and `git_commit.txt` into its results folder.

## Methods

| id | affinity | count backend | post-processing |
|---|---|---|---|
| `baseline_mode` | — | most common K of the training split | — |
| `nmesc_ecapa` | raw ECAPA | exact eigh | none (old best, reproduced exactly) |
| `nmesc_ecapa_pp` | raw ECAPA | exact eigh | tuned |
| `nmesc_affnet` / `_pp` | AffinityNet | exact eigh | none / tuned |
| `snet_affnet_pp` | AffinityNet | SpectralNet v2 | tuned (main proposed system) |
| `snet_ecapa_pp` | raw ECAPA | SpectralNet v2 | tuned |
