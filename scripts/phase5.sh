#!/usr/bin/env bash
# Phase 5 (SpectralNet v2) on AMI dev. Logs go to work/logs/; results to results/.
set -uo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-/home/pm_students/miniconda3/envs/spectral/bin/python}
L=work/logs
mkdir -p $L
run() { echo; echo "=== $1"; shift; "$@" 2>&1 | grep -v -i -E "warn|uem" | tee -a "$LOG"; }

LOG=$L/phase5_tests.log;   : > $LOG; run "1/5 unit tests" $PY tests/run_tests.py
LOG=$L/phase5_tune.log;    : > $LOG; run "2/5 tune snet_affnet_pp (pre-trains warm start, ~20 min)" $PY run.py tune --method snet_affnet_pp
LOG=$L/phase5_eval.log;    : > $LOG
for m in snet_ecapa_pp snet_affnet_pp; do
  run "3/5 evaluate AMI dev $m" $PY run.py evaluate --config configs/ami_dev.yaml --method $m
done
run "4/5 evaluate AMI dev snet_affnet_pp, warm start OFF" $PY run.py evaluate --config configs/ami_dev.yaml \
    --method snet_affnet_pp --set spectralnet.warm_start=false --set method.tag=no_warm
LOG=$L/phase5_oos.log;     : > $LOG; run "5/5 out-of-sample test" $PY scripts/spectralnet_oos.py --config configs/ami_dev.yaml --method snet_affnet_pp
echo; echo "=== Phase 5 done"
