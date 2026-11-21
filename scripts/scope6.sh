#!/usr/bin/env bash
# Phase 9 — scope 1-6 speakers. snet_ecapa_pp (main) and nmesc_ecapa_pp (ablation: same tuning, exact backend).
# Tuning sets (no test data): AMI dev + AMI train (snet/nmesc_ecapa have no trained parts that saw AMI train;
# AffinityNet is not used) + VoxConverse train and val restricted to 1-6 speakers.
# Grid: k_max {6,8} x p_min {1,2,3,4,6} x pruning (off | absolute | relative | segments) x merge x single.
# Objective: worst-corpus exact accuracy (target "at least X % on every corpus"), ties -> mean exact, MAE.
# Tests, each run once at the end: VoxConverse test 1-6 speakers (117), AMI test (16), VoxConverse test all (232).
#   setsid nohup ./scripts/scope6.sh > work/logs/scope6.out 2>&1 < /dev/null & disown
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-/home/pm_students/miniconda3/envs/spectral/bin/python}
LOGD=work/logs/scope6; mkdir -p $LOGD
STATUS=$LOGD/STATUS.md
echo "# Scope 1-6 speakers — $(date) (git $(git rev-parse --short HEAD))" > $STATUS
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
TUNE=(--set tuning.out_dir=results/tuning_k6
      --set "tuning.val_configs=[configs/ami_dev.yaml,configs/ami_train.yaml,configs/vox_train_k6.yaml,configs/vox_val_k6.yaml]"
      --set "tuning.k_max=[6,8]" --set "tuning.p_min=[1,2,3,4,6]"
      --set "tuning.min_cluster_share=[0.0,0.01,0.02,0.03,0.05,0.07]"
      --set "tuning.min_cluster_share_rel=[0.05,0.1,0.15,0.2,0.3]"
      --set "tuning.min_cluster_segments=[3,5,10,20,40]"
      --set tuning.objective=worst_exact --set spectralnet.warm_start=false)
EV() { echo "--set method.tag=$2 --set postprocess.tuned_file=results/tuning_k6/$1/best.yaml --set spectralnet.warm_start=false"; }

# main model
step "tune snet_ecapa_pp" $PY run.py tune --method snet_ecapa_pp "${TUNE[@]}"
step "vox test k6 snet_ecapa_pp" $PY run.py evaluate --config configs/vox_test_k6.yaml --method snet_ecapa_pp $(EV snet_ecapa_pp scope6)
step "ami test snet_ecapa_pp"    $PY run.py evaluate --config configs/ami_test.yaml    --method snet_ecapa_pp $(EV snet_ecapa_pp scope6)
step "vox test all snet_ecapa_pp" $PY run.py evaluate --config configs/vox_test.yaml   --method snet_ecapa_pp $(EV snet_ecapa_pp scope6_all)
# reference NME-SC with the same K cap (fair: it is also told K <= 6), and the mode baseline of the scope
for c in vox_test_k6 ami_test; do
  step "$c nmesc_ecapa k_max 6" $PY run.py evaluate --config configs/$c.yaml --method nmesc_ecapa \
       --set method.tag=scope6 --set clustering.k_max=6
done
step "vox_test_k6 baseline_mode" $PY run.py evaluate --config configs/vox_test_k6.yaml --method baseline_mode \
     --set method.tag=scope6
# ablation: same tuning with the exact eigensolver instead of SpectralNet
step "tune nmesc_ecapa_pp" $PY run.py tune --method nmesc_ecapa_pp "${TUNE[@]}"
step "vox test k6 nmesc_ecapa_pp" $PY run.py evaluate --config configs/vox_test_k6.yaml --method nmesc_ecapa_pp $(EV nmesc_ecapa_pp scope6)
step "ami test nmesc_ecapa_pp"    $PY run.py evaluate --config configs/ami_test.yaml    --method nmesc_ecapa_pp $(EV nmesc_ecapa_pp scope6)
step "report" $PY scripts/scope6_report.py
echo "[$(date +%H:%M)] ALL DONE"; echo "" >> $STATUS; echo "Finished $(date)" >> $STATUS
