#!/usr/bin/env bash
set -euo pipefail
pip install --upgrade pip
pip install -r requirements-prod.txt
cd Movie_Recommend_System/backend
test -f artifacts/v1/manifest.json || python scripts/train_models.py
echo "Lean API build OK (TF-IDF + SVD artifacts, no torch install)"
