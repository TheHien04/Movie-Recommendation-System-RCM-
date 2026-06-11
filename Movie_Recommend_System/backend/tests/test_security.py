import json
from pathlib import Path

import pytest

TEST_CASES = Path(__file__).resolve().parents[2] / "data" / "test_cases.json"


def test_admin_keys_requires_auth(client):
  response = client.post("/api/admin/keys", json={"owner": "evil"})
  assert response.status_code == 403


def test_admin_keys_with_auth(client):
  response = client.post(
    "/api/admin/keys",
    json={"owner": "partner"},
    headers={"X-Admin-Key": "test-admin-key"},
  )
  assert response.status_code == 201
  payload = response.get_json()
  assert "api_key" in payload
  assert payload["key_prefix"]


def test_b2b_requires_api_key(client):
  response = client.post("/api/v1/recommend", json={"query": "horror"})
  assert response.status_code == 403


def test_b2b_with_hashed_key(client):
  create = client.post(
    "/api/admin/keys",
    json={"owner": "ci"},
    headers={"X-Admin-Key": "test-admin-key"},
  )
  api_key = create.get_json()["api_key"]
  response = client.post(
    "/api/v1/recommend",
    json={"query": "horror movies"},
    headers={"X-API-Key": api_key},
  )
  assert response.status_code == 200
  assert "recommended_movies" in response.get_json()


def test_tmdb_proxy_blocks_unknown_endpoint(client, monkeypatch):
  monkeypatch.setenv("TMDB_API_KEY", "fake-key")
  response = client.get("/api/tmdb/account")
  assert response.status_code == 403


def test_openapi_spec(client):
  response = client.get("/api/openapi.json")
  assert response.status_code == 200
  assert response.get_json()["openapi"] == "3.0.3"


def test_readiness_probe(client):
  response = client.get("/api/health/ready")
  assert response.status_code in (200, 503)
  payload = response.get_json()
  assert "checks" in payload
