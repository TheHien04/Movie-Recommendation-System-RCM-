# Cinemate — Production Deploy Checklist

## URLs

| Environment | URL |
|-------------|-----|
| **Unified (recommended)** | https://cinemate-live.onrender.com |
| **GitHub Pages (static)** | https://thehien04.github.io/Movie-Recommendation-System-RCM-/ |

## One-time Render setup

1. [Render Dashboard](https://dashboard.render.com) → **New Blueprint** → connect repo `TheHien04/Movie-Recommendation-System-RCM-`
2. **Manual Sync** after each `render.yaml` change on `main`
3. Set secrets in service **Environment**:
   - `TMDB_API_KEY` (required — posters & trending)
   - `OPENAI_API_KEY` (optional — richer RAG answers)
4. Postgres `cinemate-db` is provisioned automatically via `render.yaml` (`DATABASE_URL` linked)

## GitHub Pages

1. Repo **Settings → Pages** → Source: branch `gh-pages` / root
2. Auto-deployed on push to `main` via `.github/workflows/pages.yml`

## Verify production

```bash
curl https://cinemate-live.onrender.com/api/health/live
curl https://cinemate-live.onrender.com/api/health/ready
```

First request after idle may take 30–90s (Render free tier cold start).

## Local parity

```bash
cd Movie_Recommend_System/backend && source .venv/bin/activate && python app.py
cd Movie_Recommend_System/web && npm run dev
```
