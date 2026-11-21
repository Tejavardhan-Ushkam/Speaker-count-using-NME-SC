#!/usr/bin/env bash
# snet_ecapa_pp trained on VoxConverse: SpectralNet warm-start network pre-trained on VoxConverse train
# (173 recordings, 50 steps each; created automatically as checkpoints/spectralnet/pretrained_ecapa_unnormalized_m26.pt,
# AMI's m11 net is untouched), then pruning + p_min re-tuned on AMI dev + Vox val with warm start ON,
# then tested on VoxConverse test and AMI test. Nothing is tuned on test.
# Tuned values -> results/tuning_vox_warm/snet_ecapa_pp/best.yaml ; test -> results/<corpus>/test/snet_ecapa_pp/vox_warm/
#   setsid nohup ./scripts/vox_snet_warm.sh > work/logs/vox_snet_warm.out 2>&1 < /dev/null & disown
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-/home/pm_students/miniconda3/envs/spectral/bin/python}
LOGD=work/logs/vox_snet_warm; mkdir -p $LOGD
STATUS=$LOGD/STATUS.md
echo "# snet_ecapa_pp, Vox warm start — $(date) (git $(git rev-parse --short HEAD))" > $STATUS
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
M=snet_ecapa_pp
step "tune $M (warm start; pre-trains on Vox train first)" $PY run.py tune --method $M \
     --set tuning.out_dir=results/tuning_vox_warm --set "tuning.p_min=[1,2,3,4,5,6,8]" \
     --set "tuning.min_cluster_share_rel=[0.05,0.1,0.15,0.2,0.3,0.4]" --set spectralnet.warm_start=true
EV=(--set method.tag=vox_warm --set postprocess.tuned_file=results/tuning_vox_warm/$M/best.yaml
    --set spectralnet.warm_start=true)
step "vox test $M" $PY run.py evaluate --config configs/vox_test.yaml --method $M "${EV[@]}"
step "ami test $M" $PY run.py evaluate --config configs/ami_test.yaml --method $M "${EV[@]}"
echo "[$(date +%H:%M)] ALL DONE"; echo "" >> $STATUS; echo "Finished $(date)" >> $STATUS
