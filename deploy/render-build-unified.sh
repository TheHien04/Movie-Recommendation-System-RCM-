#!/usr/bin/env bash
set -euo pipefail

echo "=== Install Python dependencies ==="
pip install --upgrade pip
pip install flask flask-cors flask-sqlalchemy pandas numpy scipy scikit-learn joblib requests python-dotenv openai PyJWT gunicorn sentence-transformers torch sentry-sdk

echo "=== Build React frontend (same-origin API) ==="
cd Movie_Recommend_System/web
npm ci
VITE_API_URL= npm run build

echo "=== Verify ML artifacts ==="
cd ../backend
if [ ! -f artifacts/v1/manifest.json ]; then
  python scripts/train_models.py
fi
echo "Build complete — Flask will serve web/dist + API"
