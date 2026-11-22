#!/usr/bin/env bash
# Assemble deploy/space_build/: everything the Hugging Face Docker Space needs, and nothing else
# (no datasets, no results, no training checkpoints). Push that folder to the Space's git repo.
#   ./deploy/build_space.sh
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=deploy/space_build
rm -rf "$OUT"; mkdir -p "$OUT/configs" "$OUT/deploy"
cp deploy/hf_space/{app.py,Dockerfile,requirements.txt,README.md} "$OUT/"
rsync -a --exclude __pycache__ --exclude '*.pyc' speakercount "$OUT/"
cp configs/base.yaml "$OUT/configs/"; cp -r configs/methods "$OUT/configs/"
cp deploy/tuned.yaml "$OUT/deploy/tuned.yaml"
VER=$(git rev-parse --short HEAD)
{ cat deploy/model.yaml; echo "version: \"$VER\""; } > "$OUT/deploy/model.yaml"
printf '__pycache__/\n*.pyc\n' > "$OUT/.gitignore"
echo "Built $OUT (code version $VER):"; du -sh "$OUT"; find "$OUT" -maxdepth 2 | sort | head -30
