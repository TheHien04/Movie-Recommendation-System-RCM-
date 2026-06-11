#!/usr/bin/env bash
set -euo pipefail

echo "=== Python deps (lean, no torch) ==="
pip install --upgrade pip
pip install -r requirements-prod.txt

echo "=== Build React (same-origin API) ==="
cd Movie_Recommend_System/web
npm ci
VITE_API_URL= npm run build
cp dist/index.html dist/404.html
touch dist/.nojekyll

echo "=== Verify ML artifacts ==="
cd ../backend
test -f artifacts/v1/manifest.json
echo "Unified build OK"
