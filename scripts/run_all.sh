#!/usr/bin/env bash
# End-to-end pipeline (prompt §8.2). Steps whose data is missing (VoxConverse, for now) are
# skipped: `prepare` on an unavailable split is skipped here, and tune/train skip it themselves.
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-python}

have() {  # does this split's data exist?
  $PY - "$1" <<'EOF'
import sys
from speakercount.config import load_config
from speakercount.rttm import is_available
sys.exit(0 if is_available(load_config(sys.argv[1])) else 1)
EOF
}

$PY run.py check-data || true
[ -d dataset/voxconverse/rttm/dev ] && $PY run.py make-splits
for c in ami_train ami_dev ami_test vox_train vox_val vox_test; do
  if have configs/$c.yaml; then $PY run.py prepare --config configs/$c.yaml; else echo "skip prepare $c (no data)"; fi
done
$PY run.py train-affnet --config configs/affnet_train.yaml
for m in nmesc_ecapa_pp nmesc_affnet_pp snet_affnet_pp snet_ecapa_pp; do $PY run.py tune --method $m; done
for c in ami_test vox_test; do
  have configs/$c.yaml || { echo "skip evaluate $c (no data)"; continue; }
  for m in baseline_mode nmesc_ecapa nmesc_ecapa_pp nmesc_affnet nmesc_affnet_pp snet_affnet_pp snet_ecapa_pp; do
    $PY run.py evaluate --config configs/$c.yaml --method $m
  done
done
# realistic VAD
for c in ami_test_pyannote vox_test_pyannote; do
  have configs/$c.yaml || { echo "skip $c (no data)"; continue; }
  $PY run.py prepare --config configs/$c.yaml
  for m in nmesc_ecapa snet_affnet_pp; do $PY run.py evaluate --config configs/$c.yaml --method $m; done
done
$PY run.py compare
$PY run.py plots
