# Cinemate — Production-Grade ML Movie Platform

[![CI](https://github.com/TheHien04/Movie-Recommendation-System-RCM-/actions/workflows/ci.yml/badge.svg)](https://github.com/TheHien04/Movie-Recommendation-System-RCM-/actions/workflows/ci.yml)

Full-stack movie discovery with **Hybrid ML v2**, **RAG chat**, personalization, A/B testing, MLOps artifacts, and B2B API.

## Quality Scorecard (10/10 target)

| Area | Status |
|------|--------|
| Hybrid ML v3 (Transformer + SVD + NeuMF PyTorch) | ✅ |
| Hyperparameter tuning (grid-search NDCG) | ✅ |
| MLOps (train script, versioned artifacts, model card) | ✅ |
| Security (JWT, auth rate limits, password policy, HSTS/CSP) | ✅ |
| CI (ruff, pytest 45%+ cov, vitest, Docker build) | ✅ |
| OpenAPI 3.0 + health probes (live/ready) | ✅ |
| PWA + SEO meta + error boundary | ✅ |
| Watchlist (local + cloud sync + batch API) | ✅ |
| Deploy (Render unified + Postgres + GH Pages + Docker) | ✅ |
| Personalization (ratings/watchlist → ML) + chat cloud sync | ✅ |

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 19, Vite 8, TypeScript, Tailwind 4 |
| Backend | Flask, SQLAlchemy, JWT, gunicorn |
| ML | TF-IDF / Sentence-Transformers, SVD-CF, Hybrid, MMR |
| Ops | GitHub Actions, Docker, Render, Vercel |

## Quick Start

```bash
# 1. Backend
cd Movie_Recommend_System/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r ../../requirements.txt
cp .env.example .env
python scripts/train_models.py
python app.py                    # http://127.0.0.1:5001

# 2. Frontend
cd Movie_Recommend_System/web
npm install && npm run dev       # http://127.0.0.1:5173
```

## Tests

```bash
# Backend (42+ tests)
cd Movie_Recommend_System/backend
pytest -q --cov=app --cov-fail-under=45

# Frontend
cd Movie_Recommend_System/web
npm run lint && npm run test && npm run build

# Docker
docker compose up --build
```

## Key API Routes

| Route | Description |
|-------|-------------|
| `GET /api/health/ready` | Readiness probe (DB + dataset + artifacts) |
| `POST /recommend` | Hybrid or RAG recommendations |
| `GET /api/search?q=` | Semantic search |
| `POST /api/movies/batch` | Bulk poster/metadata for watchlist |
| `GET /api/ml/evaluate` | Offline NDCG benchmark |
| `GET /api/openapi.json` | OpenAPI 3.0 spec |
| `POST /api/v1/recommend` | B2B API (`X-API-Key`) |

## Deploy (Production)

### Unified app — Render (recommended)
1. Connect repo on [Render](https://render.com) and **Manual Sync** `render.yaml`
2. Live URL: **https://cinemate-live.onrender.com** (API + SPA same origin)
3. Set secrets in Render dashboard: `TMDB_API_KEY`, optional `OPENAI_API_KEY`, `DATABASE_URL`

### Frontend — GitHub Pages (optional static mirror)
- **https://thehien04.github.io/Movie-Recommendation-System-RCM-/**
- Enable Pages → branch `gh-pages` in repo Settings
- Static build calls API at `cinemate-live.onrender.com` via `runtime-api.ts`

### Docker
```bash
docker build -t cinemate-api .
docker run -p 5001:5001 -e TMDB_API_KEY=xxx cinemate-api
```

## Documentation

- [DEPLOY.md](DEPLOY.md) — Production deploy checklist
- [RESULTS.md](RESULTS.md) — Offline eval & personalization notes
- [MODEL_CARD.md](MODEL_CARD.md) — ML model documentation
- [SECURITY.md](SECURITY.md) — Security policy
- [CONTRIBUTING.md](CONTRIBUTING.md) — Dev workflow

## Project Structure

```
Movie_Recommend_System/
├── backend/          # Flask API + ML + artifacts/
├── web/              # React frontend (active)
├── data/             # ML eval test cases
├── frontend/         # ARCHIVED legacy UI
└── notebooks/        # ML experiments
```

## License

MIT — see [LICENSE](LICENSE)
