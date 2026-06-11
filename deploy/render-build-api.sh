#!/usr/bin/env bash
set -euo pipefail
pip install --upgrade pip
pip install -r requirements.txt
cd Movie_Recommend_System/backend
if [ -f artifacts/v1/manifest.json ]; then
  echo "ML artifacts found — skipping offline training"
else
  python scripts/train_models.py
fi
