#!/usr/bin/env bash
# Unattended run: rest of Phase 5 (AMI dev) + Phase 6 (AMI test, ablations, pyannote VAD).
# Every step is independent: a failure is logged and the script moves on.
# All selection/tuning was done on AMI dev before this script; test runs only evaluate.
#
#   nohup ./scripts/overnight.sh > work/logs/overnight.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-/home/pm_students/miniconda3/envs/spectral/bin/python}
LOGD=work/logs/overnight
mkdir -p $LOGD
STATUS=$LOGD/STATUS.md
echo "# Overnight run $(date)  (git $(git rev-parse --short HEAD))" > $STATUS
echo "| # | step | result | minutes |" >> $STATUS; echo "|---|---|---|---|" >> $STATUS
N=0
step() {  # step "name" cmd...
  N=$((N+1)); local name=$1; shift
  local log=$LOGD/$(printf "%02d" $N)_$(echo "$name" | tr ' /=' '___').log
  echo "[$(date +%H:%M)] START $N $name"
  local t0=$(date +%s)
  "$@" > "$log" 2>&1
  local rc=$?
  local mins=$(( ($(date +%s) - t0) / 60 ))
  if [ $rc -eq 0 ]; then r=ok; else r="**FAILED** (rc $rc, see $(basename $log))"; fi
  echo "| $N | $name | $r | $mins |" >> $STATUS
  echo "[$(date +%H:%M)] END   $N $name -> $r"
}
ev()  { $PY run.py evaluate "$@"; }

# ---------------- Phase 5 (AMI dev) ----------------
step "tune snet_affnet_pp"            $PY run.py tune --method snet_affnet_pp
step "dev snet_affnet_pp"             ev --config configs/ami_dev.yaml --method snet_affnet_pp --force
step "dev snet_affnet_pp no_warm"     ev --config configs/ami_dev.yaml --method snet_affnet_pp --force --set spectralnet.warm_start=false --set method.tag=no_warm
step "oos snet_affnet_pp"             $PY scripts/spectralnet_oos.py --config configs/ami_dev.yaml --method snet_affnet_pp

# ---------------- Phase 6: AMI test, all methods ----------------
for m in baseline_mode nmesc_ecapa nmesc_ecapa_pp nmesc_affnet nmesc_affnet_pp snet_affnet_pp snet_ecapa_pp; do
  step "test $m" ev --config configs/ami_test.yaml --method $m --force
done
step "test snet_affnet_pp no_warm"    ev --config configs/ami_test.yaml --method snet_affnet_pp --force --set spectralnet.warm_start=false --set method.tag=no_warm

# ---------------- Phase 6: inference-time ablations (dev + test) ----------------
# compared on the no-post-processing methods so the effect is not hidden by pruning/merging
for split in dev test; do
  for m in nmesc_ecapa nmesc_affnet; do
    step "$split $m lap_symnorm" ev --config configs/ami_$split.yaml --method $m --force --set clustering.laplacian=sym_norm --set method.tag=lap_symnorm
    step "$split $m refine"      ev --config configs/ami_$split.yaml --method $m --force --set affinity.refine=true --set method.tag=refine
    step "$split $m ORACLE_overlap_removal" ev --config configs/ami_$split.yaml --method $m --force --set affinity.oracle_overlap_removal=true --set method.tag=oracle_overlap_removal
  done
done

# ---------------- Phase 6: training ablations (retrain, select on AMI dev, evaluate nmesc_affnet) ----------------
train_abl() {  # tag, overrides...
  local tag=$1; shift
  step "train affnet $tag" $PY run.py train-affnet --config configs/affnet_train.yaml --set affnet.out_dir=checkpoints/affnet_$tag "$@"
  if [ -f checkpoints/affnet_$tag/best.pt ]; then
    for split in dev test; do
      step "$split nmesc_affnet $tag" ev --config configs/ami_$split.yaml --method nmesc_affnet --force \
        --set affinity.checkpoint=checkpoints/affnet_$tag/best.pt --set method.tag=$tag
    done
  fi
}
train_abl ctx0          --set affnet.n_layers=0
train_abl no_time       --set affnet.time_encoding=false
train_abl no_spkdrop    --set affnet.speaker_dropout=0.0
train_abl bce_only      --set affnet.loss_supcon_weight=0.0
train_abl most_overlap  --set affnet.label_mode=most_overlap
# old Siamese with flaws 1-2 fixed only
step "train siamese_fixed" $PY run.py train-affnet --config configs/affnet_train.yaml --set affnet.arch=siamese --set affnet.out_dir=checkpoints/siamese_fixed
if [ -f checkpoints/siamese_fixed/best.pt ]; then
  for split in dev test; do
    step "$split siamese_fixed" ev --config configs/ami_$split.yaml --method nmesc_affnet --force \
      --set affinity.source=siamese --set affinity.checkpoint=checkpoints/siamese_fixed/best.pt --set method.tag=siamese_fixed
  done
fi

# ---------------- Phase 6: realistic VAD (pyannote/segmentation-3.0; needs HF access to the gated model) ----------------
step "prepare ami_test_pyannote" $PY run.py prepare --config configs/ami_test_pyannote.yaml
if [ -d work/ami/test_pyannote/embeddings ]; then
  for m in nmesc_ecapa snet_affnet_pp; do step "test_pyannote $m" ev --config configs/ami_test_pyannote.yaml --method $m --force; done
fi

step "unit tests" $PY tests/run_tests.py
echo "[$(date +%H:%M)] ALL DONE" ; echo "" >> $STATUS; echo "Finished $(date)" >> $STATUS
