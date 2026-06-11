import json
from pathlib import Path

import pytest

from app.ml.hybrid import HybridRecommender
from app.ml.metrics import evaluate_ranking

TEST_CASES = Path(__file__).resolve().parents[2] / "data" / "test_cases.json"
MIN_AVG_NDCG = 0.08
K = 5


@pytest.fixture(scope="module")
def cases():
  return json.loads(TEST_CASES.read_text(encoding="utf-8"))


def test_offline_eval_ndcg_gate(cases):
  hybrid = HybridRecommender()
  scores = []
  for case in cases:
    ranked = hybrid.recommend(case["input"], top_n=K)
    titles = [row["title"] for row in ranked]
    metrics = evaluate_ranking(titles, case.get("expected_movies", []), k=K)
    scores.append(metrics[f"ndcg@{K}"])

  avg_ndcg = sum(scores) / len(scores)
  assert avg_ndcg >= MIN_AVG_NDCG, f"avg NDCG@{K}={avg_ndcg:.4f} below gate {MIN_AVG_NDCG}"


def test_ml_evaluate_endpoint(client):
  response = client.get("/api/ml/evaluate")
  assert response.status_code == 200
  payload = response.get_json()
  assert payload["cases"] >= 8
  assert payload["avg_ndcg"] >= MIN_AVG_NDCG
