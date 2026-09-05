import pytest
from bson import ObjectId
from backend.core.security import create_access_token, hash_password
from backend.tests.conftest import test_db


@pytest.fixture
def auth_user():
    user_id = str(ObjectId())
    user_doc = {
        "_id": ObjectId(user_id),
        "id": user_id,
        "name": "Test User",
        "email": "testuser@example.com",
        "password_hash": hash_password("Password123"),
        "is_active": True,
    }
    test_db.users.insert_one(user_doc)
    token = create_access_token(user_id)
    return {"user_id": user_id, "token": token}


def test_list_documents_unauthorized(client):
    response = client.get("/api/documents")
    assert response.status_code == 401


def test_list_documents_empty(client, auth_user):
    response = client.get(
        "/api/documents",
        headers={"Authorization": f"Bearer {auth_user['token']}"},
    )
    assert response.status_code == 200
    assert response.json() == []


def test_get_document_not_found(client, auth_user):
    random_oid = str(ObjectId())
    response = client.get(
        f"/api/documents/{random_oid}",
        headers={"Authorization": f"Bearer {auth_user['token']}"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_get_document_invalid_id(client, auth_user):
    response = client.get(
        "/api/documents/invalid-id",
        headers={"Authorization": f"Bearer {auth_user['token']}"},
    )
    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]
