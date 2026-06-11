#!/usr/bin/env bash
set -euo pipefail
cd Movie_Recommend_System/web
npm ci
export VITE_API_URL="https://cinemate-rcm-api.onrender.com"
export VITE_BASE_PATH="/"
echo "Building static web → API ${VITE_API_URL}"
npm run build
# SPA fallback for Render static hosting
printf '/*\t/index.html\t200\n' > dist/_redirects
