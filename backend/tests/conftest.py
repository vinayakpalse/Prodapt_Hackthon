import pytest
from fastapi.testclient import TestClient
import mongomock

from backend.main import app
from backend.database.database import get_db, init_db

mock_client = mongomock.MongoClient()
test_db = mock_client["test_db"]


def override_get_db():
    return test_db


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_database():
    """Clear MongoDB collections before and after each test."""
    test_db.users.drop()
    test_db.refresh_tokens.drop()
    test_db.documents.drop()
    init_db(test_db)
    yield
    test_db.users.drop()
    test_db.refresh_tokens.drop()
    test_db.documents.drop()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    return test_db
