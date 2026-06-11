import os
import sys

import pytest

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault("FLASK_ENV", "testing")
os.environ["ADMIN_API_KEY"] = "test-admin-key"
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci-only")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")


@pytest.fixture
def client():
  from app import create_app

  app = create_app()
  app.config["TESTING"] = True
  with app.test_client() as test_client:
    yield test_client
