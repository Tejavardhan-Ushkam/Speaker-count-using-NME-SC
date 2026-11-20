#!/usr/bin/env bash
# Tune pruning (+ NME-SC p_min) on AMI dev + VoxConverse val, then test on VoxConverse test and AMI test.
# Methods: nmesc_ecapa_pp, snet_ecapa_pp (raw ECAPA; no AffinityNet). Nothing is tuned on test.
# Tuned values -> results/tuning_vox/<method>/best.yaml (AMI-only values in results/tuning/ are untouched).
# Test results -> results/<corpus>/test/<method>/vox_tuned/
#   setsid nohup ./scripts/vox_prune.sh > work/logs/vox_prune.out 2>&1 < /dev/null & disown
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-/home/pm_students/miniconda3/envs/spectral/bin/python}
LOGD=work/logs/vox_prune; mkdir -p $LOGD
STATUS=$LOGD/STATUS.md
echo "# Vox-tuned pruning — $(date) (git $(git rev-parse --short HEAD))" > $STATUS
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
TUNE=(--set tuning.out_dir=results/tuning_vox --set "tuning.p_min=[1,2,3,4,5,6,8]"
      --set "tuning.min_cluster_share_rel=[0.05,0.1,0.15,0.2,0.3,0.4]" --set spectralnet.warm_start=false)
EVAL() { echo "--set method.tag=vox_tuned --set postprocess.tuned_file=results/tuning_vox/$1/best.yaml --set spectralnet.warm_start=false"; }

step "prepare vox_val"   $PY run.py prepare --config configs/vox_val.yaml
step "prepare vox_train" $PY run.py prepare --config configs/vox_train.yaml
for m in nmesc_ecapa_pp snet_ecapa_pp; do
  step "tune $m" $PY run.py tune --method $m "${TUNE[@]}"
done
for m in nmesc_ecapa_pp snet_ecapa_pp; do
  step "vox test $m" $PY run.py evaluate --config configs/vox_test.yaml --method $m $(EVAL $m)
  step "ami test $m" $PY run.py evaluate --config configs/ami_test.yaml --method $m $(EVAL $m)
done
# fair VoxConverse baseline: most common K of VoxConverse train
step "vox test baseline_mode (Vox mode)" $PY run.py evaluate --config configs/vox_test.yaml --method baseline_mode \
     --set method.tag=vox_trained --set dataset.train_config=configs/vox_train.yaml
echo "[$(date +%H:%M)] ALL DONE"; echo "" >> $STATUS; echo "Finished $(date)" >> $STATUS
