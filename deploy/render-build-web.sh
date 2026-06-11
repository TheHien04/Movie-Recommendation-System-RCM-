#!/usr/bin/env bash
set -euo pipefail
cd Movie_Recommend_System/web
npm ci
if [ -z "${CINEMATE_API_HOST:-}" ]; then
  echo "CINEMATE_API_HOST is required for production web build"
  exit 1
fi
export VITE_API_URL="https://${CINEMATE_API_HOST}"
echo "Building web with VITE_API_URL=${VITE_API_URL}"
npm run build
