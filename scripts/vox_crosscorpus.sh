#!/usr/bin/env bash
# Step 1 of the VoxConverse work: CROSS-CORPUS test. Models, thresholds and the mode baseline all
# come from AMI only (git tag ami-only-v1); nothing is fitted or tuned on VoxConverse.
# Results: results/voxconverse/test/<method>/ami_trained/
#   nohup ./scripts/vox_crosscorpus.sh > work/logs/vox_crosscorpus.out 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-/home/pm_students/miniconda3/envs/spectral/bin/python}
LOGD=work/logs/vox_crosscorpus; mkdir -p $LOGD
STATUS=$LOGD/STATUS.md
echo "# VoxConverse test, AMI-trained models — $(date) (git $(git rev-parse --short HEAD))" > $STATUS
echo "| # | step | result | minutes |" >> $STATUS; echo "|---|---|---|---|" >> $STATUS
N=0
step() {
  N=$((N+1)); local name=$1; shift
  local log=$LOGD/$(printf "%02d" $N)_$(echo "$name" | tr ' /=' '___').log
  echo "[$(date +%H:%M)] START $N $name"; local t0=$(date +%s)
  "$@" > "$log" 2>&1; local rc=$?
  local r=ok; [ $rc -ne 0 ] && r="**FAILED** (rc $rc, see $(basename $log))"
  echo "| $N | $name | $r | $(( ($(date +%s) - t0) / 60 )) |" >> $STATUS
  echo "[$(date +%H:%M)] END   $N $name -> $r"
}
AMI=(--set method.tag=ami_trained --set affinity.checkpoint=checkpoints/affnet_ami_only/best.pt
     --set spectralnet.warm_start=false)   # warm-start net exists only for AMI's k_max (m=11); no effect on AMI anyway
tuned() { echo "--set postprocess.tuned_file=results/tuning_ami_only/$1/best.yaml"; }

step "prepare vox_test (oracle VAD)" $PY run.py prepare --config configs/vox_test.yaml
step "test baseline_mode (AMI mode = 4)" $PY run.py evaluate --config configs/vox_test.yaml --method baseline_mode \
     --set method.tag=ami_trained --set dataset.train_config=configs/ami_train.yaml
for m in nmesc_ecapa nmesc_affnet; do
  step "test $m" $PY run.py evaluate --config configs/vox_test.yaml --method $m "${AMI[@]}"
done
for m in nmesc_ecapa_pp nmesc_affnet_pp snet_ecapa_pp snet_affnet_pp; do
  step "test $m" $PY run.py evaluate --config configs/vox_test.yaml --method $m "${AMI[@]}" $(tuned $m)
done
# realistic VAD
step "prepare vox_test_pyannote" $PY run.py prepare --config configs/vox_test_pyannote.yaml
step "test_pyannote nmesc_ecapa" $PY run.py evaluate --config configs/vox_test_pyannote.yaml --method nmesc_ecapa "${AMI[@]}"
step "test_pyannote snet_affnet_pp" $PY run.py evaluate --config configs/vox_test_pyannote.yaml --method snet_affnet_pp "${AMI[@]}" $(tuned snet_affnet_pp)
echo "[$(date +%H:%M)] ALL DONE"; echo "" >> $STATUS; echo "Finished $(date)" >> $STATUS
