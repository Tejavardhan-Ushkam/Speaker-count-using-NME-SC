#!/usr/bin/env bash
# Assemble deploy/space_build/: everything the Hugging Face Docker Space needs, and nothing else
# (no datasets, no results, no training checkpoints). Push that folder to the Space's git repo.
#   ./deploy/build_space.sh
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=deploy/space_build
mkdir -p "$OUT"; find "$OUT" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +   # keep the Space git repo
mkdir -p "$OUT/configs" "$OUT/deploy"
cp deploy/hf_space/{app.py,app_core.py,requirements.txt,packages.txt,README.md} "$OUT/"   # Gradio + ZeroGPU Space
# (the Docker variant for paid CPU hardware lives in deploy/hf_space_docker/)
rsync -a --exclude __pycache__ --exclude '*.pyc' speakercount "$OUT/"
cp configs/base.yaml "$OUT/configs/"; cp -r configs/methods "$OUT/configs/"
if [ -f deploy/tuned.yaml ]; then cp deploy/tuned.yaml "$OUT/deploy/tuned.yaml"; fi   # only for methods with post-processing
VER=$(git rev-parse --short HEAD)
{ cat deploy/model.yaml; echo "version: \"$VER\""; } > "$OUT/deploy/model.yaml"
printf '__pycache__/\n*.pyc\n' > "$OUT/.gitignore"
echo "Built $OUT (code version $VER):"; du -sh "$OUT"; find "$OUT" -maxdepth 2 | sort | head -30
