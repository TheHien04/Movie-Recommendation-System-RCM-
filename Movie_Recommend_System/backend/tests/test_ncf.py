import pytest

from app.ml.interaction_data import build_implicit_interactions


def test_implicit_interactions_shape():
  u, i, y, user_keys, titles = build_implicit_interactions()
  assert len(u) == len(i) == len(y)
  assert len(u) > 100
  assert len(user_keys) > 5
  assert len(titles) > 100


@pytest.mark.skipif(
  __import__("importlib").util.find_spec("torch") is None,
  reason="PyTorch not installed",
)
def test_ncf_train_and_recommend():
  from app.ml.ncf import NeuralCFRecommender, train_ncf

  report = train_ncf(epochs=2)
  assert report.get("trained") is True

  ncf = NeuralCFRecommender()
  assert ncf.available
  scores = ncf.recommend_from_query("horror movies", top_n=5)
  assert len(scores) > 0
