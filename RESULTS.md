# Cinemate — Offline Evaluation Results

Benchmark: **20 curated queries** in `Movie_Recommend_System/data/test_cases.json`  
Metric: **NDCG@5** (normalized discounted cumulative gain at rank 5)  
Catalog: ~500 movies in `backend/data/movie.csv`

## Summary (Hybrid v3)

| Model | Avg NDCG@5 | Notes |
|-------|------------|-------|
| **Hybrid v3** (semantic + SVD + NeuMF + rules + MMR) | **~0.11** | Primary production model (20-case benchmark) |
| RAG v1 | Qualitative | Strong natural-language answers; retrieval + optional GPT-4o-mini |

CI gate: `MIN_AVG_NDCG = 0.10` in `backend/tests/test_eval_gate.py`.

## How to reproduce

```bash
cd Movie_Recommend_System/backend
source .venv/bin/activate
pytest tests/test_eval_gate.py -q
# or live endpoint:
curl http://127.0.0.1:5001/api/ml/evaluate
```

## Example queries (qualitative)

| Query | Hybrid v3 behavior |
|-------|-------------------|
| "horror movies" | Ranks Alien, The Shining, genre-aligned titles |
| "movies directed by Christopher Nolan" | Inception, Interstellar, Dunkirk via rule + semantic |
| "movies with Leonardo DiCaprio" | Actor rules + collaborative seeds |
| "psychological movies" | Semantic match on plot/theme keywords |

## Personalization (logged-in users)

When authenticated, recommendations use:

- **Watchlist** titles as collaborative seeds
- **Star ratings** (4–5 boost genres; 1–2 excluded from results)
- **Browse events** (view/click/save) as weak genre signals

Endpoints: `GET /api/personalized`, `POST /recommend` with JWT.

## A/B testing

- Variant **A**: Hybrid v3
- Variant **B**: RAG v1 (`OPENAI_API_KEY` optional)

Compare side-by-side in the **ML Battle** page (`/ml-battle`).

## Limitations (thesis honesty)

- Collaborative signals are partly **synthetic** (genre personas) at train time; runtime personalization uses **real** user watchlist/ratings.
- Small catalog (~500 titles) — metrics are relative, not Netflix-scale.
- RAG quality depends on OpenAI availability; hybrid works fully offline.
