"""Offline evaluation with Precision@K, Recall@K, NDCG@K, and MAP."""
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent.absolute()
sys.path.append(str(ROOT / "backend"))

from app.ml.metrics import evaluate_ranking  # noqa: E402
from app.services.top5movie_service import recommend_movies  # noqa: E402


def load_test_cases(file_path: Path):
  with open(file_path, "r", encoding="utf-8") as handle:
    return json.load(handle)


def run_evaluation(test_cases, k: int = 5):
  results = []
  for idx, case in enumerate(test_cases):
    start = time.time()
    try:
      recommendations = recommend_movies(case["input"])
      recommended_titles = [movie["title"] for movie in recommendations]
      metrics = evaluate_ranking(recommended_titles, case.get("expected_movies", []), k=k)
      results.append({
        "test_case": case["input"],
        **metrics,
        "response_time": round(time.time() - start, 2),
        "recommended": recommended_titles,
        "expected": case.get("expected_movies", []),
      })
    except Exception as exc:
      results.append({"test_case": case["input"], "error": str(exc)})

    if (idx + 1) % 3 == 0:
      print(f"Processed {idx + 1}/{len(test_cases)}")
  return results


def generate_report(results, k: int = 5):
  df = pd.DataFrame(results)
  success = [row for row in results if "error" not in row]
  summary = {
    "total_cases": len(results),
    "success_rate": len(success) / len(results) if results else 0,
    f"avg_precision@{k}": df[f"precision@{k}"].mean() if success else 0,
    f"avg_recall@{k}": df[f"recall@{k}"].mean() if success else 0,
    f"avg_ndcg@{k}": df[f"ndcg@{k}"].mean() if success else 0,
    "avg_map": df["map"].mean() if success else 0,
    "avg_response_time": df["response_time"].mean() if success else 0,
  }

  timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
  report_filename = ROOT / f"evaluation_report_{timestamp}.csv"
  df.to_csv(report_filename, index=False)

  print("\n=== EVALUATION RESULTS ===")
  for key, value in summary.items():
    if isinstance(value, float) and "rate" in key:
      print(f"{key}: {value:.1%}")
    elif isinstance(value, float):
      print(f"{key}: {value:.4f}")
    else:
      print(f"{key}: {value}")
  print(f"Report saved to: {report_filename}")


if __name__ == "__main__":
  test_path = ROOT / "data" / "test_cases.json"
  results = run_evaluation(load_test_cases(test_path), k=5)
  generate_report(results, k=5)
