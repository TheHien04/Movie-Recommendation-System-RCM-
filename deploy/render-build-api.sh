#!/usr/bin/env bash
set -euo pipefail
pip install --upgrade pip
# Lean prod install (skip pytest/ruff in CI tools) — keeps Render free tier build faster
pip install flask flask-cors flask-sqlalchemy pandas numpy scipy scikit-learn joblib requests python-dotenv openai PyJWT gunicorn sentence-transformers torch sentry-sdk
cd Movie_Recommend_System/backend
if [ -f artifacts/v1/manifest.json ]; then
  echo "ML artifacts found — skipping offline training"
else
  python scripts/train_models.py
fi
