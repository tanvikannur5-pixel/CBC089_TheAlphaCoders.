import os
from pathlib import Path
import pytest

# Ensure tests use an isolated SQLite test database
os.environ["DATABASE_URL"] = "sqlite:///test_intent.db"
os.environ["ADMIN_TOKEN"] = "test-admin-token"


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    test_db = Path("test_intent.db")
    if test_db.exists():
        try:
            test_db.unlink()
        except Exception:
            pass
