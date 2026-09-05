import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import mongomock
import jwt

from backend.main import app
from backend.database.database import get_db, init_db
from backend.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
)
from backend.core.config import settings

# Setup in-memory MongoDB mock client for isolated testing
mock_client = mongomock.MongoClient()
mock_db = mock_client["test_auth_db"]


def override_get_db():
    yield mock_db


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Clear MongoDB collections before each test."""
    mock_db.users.drop()
    mock_db.refresh_tokens.drop()
    init_db(mock_db)
    yield
    mock_db.users.drop()
    mock_db.refresh_tokens.drop()


@pytest.fixture
def client():
    """TestClient instance for making API requests."""
    return TestClient(app)


# =========================================================================
# TEST 1: Register valid user (Expected: 201 success)
# =========================================================================
def test_1_register_valid_user(client):
    payload = {
        "name": "Vinayak",
        "email": "vinayak@example.com",
        "password": "StrongPassword123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "vinayak@example.com"
    assert data["name"] == "Vinayak"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


# =========================================================================
# TEST 2: Register same email (Expected: 409 Conflict)
# =========================================================================
def test_2_register_duplicate_email(client):
    payload = {
        "name": "Vinayak",
        "email": "vinayak@example.com",
        "password": "StrongPassword123",
    }
    resp1 = client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/api/auth/register", json=payload)
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == "Email already registered"


# =========================================================================
# TEST 3: Login with valid credentials (Expected: access token + refresh cookie)
# =========================================================================
def test_3_login_valid_credentials(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )

    login_payload = {
        "email": "vinayak@example.com",
        "password": "StrongPassword123",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "vinayak@example.com"

    # Verify HttpOnly refresh token cookie
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] is not None


# =========================================================================
# TEST 4: Login with wrong password (Expected: 401 Unauthorized)
# =========================================================================
def test_4_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )

    wrong_payload = {
        "email": "vinayak@example.com",
        "password": "WrongPassword456",
    }
    response = client.post("/api/auth/login", json=wrong_payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


# =========================================================================
# TEST 5: Call /me with valid access token (Expected: 200 OK)
# =========================================================================
def test_5_get_me_valid_token(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    access_token = login_resp.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "vinayak@example.com"
    assert data["name"] == "Vinayak"


# =========================================================================
# TEST 6: Call /me without access token (Expected: 401 Unauthorized)
# =========================================================================
def test_6_get_me_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


# =========================================================================
# TEST 7: Call /me with invalid access token (Expected: 401 Unauthorized)
# =========================================================================
def test_7_get_me_invalid_token(client):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not.a.valid.jwt.token"},
    )
    assert response.status_code == 401


# =========================================================================
# TEST 8: Call /me with refresh token (Expected: 401 Unauthorized)
# =========================================================================
def test_8_get_me_with_refresh_token(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    refresh_token = login_resp.cookies["refresh_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert response.status_code == 401
    assert "access token required" in response.json()["detail"].lower()


# =========================================================================
# TEST 9: Call /refresh with valid refresh cookie (Expected: new access + rotated cookie)
# =========================================================================
def test_9_refresh_with_valid_cookie(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    initial_refresh_token = login_resp.cookies["refresh_token"]

    client.cookies.set("refresh_token", initial_refresh_token)
    refresh_resp = client.post("/api/auth/refresh")
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    rotated_refresh_token = refresh_resp.cookies.get("refresh_token")
    assert rotated_refresh_token is not None
    assert rotated_refresh_token != initial_refresh_token


# =========================================================================
# TEST 10: Use old refresh token after rotation (Expected: 401 Unauthorized)
# =========================================================================
def test_10_reuse_old_refresh_token(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    old_refresh_token = login_resp.cookies["refresh_token"]

    # Rotate once
    client.cookies.set("refresh_token", old_refresh_token)
    refresh_resp1 = client.post("/api/auth/refresh")
    assert refresh_resp1.status_code == 200

    # Attempt to reuse old token
    client.cookies.set("refresh_token", old_refresh_token)
    refresh_resp2 = client.post("/api/auth/refresh")
    assert refresh_resp2.status_code == 401
    assert "reuse" in refresh_resp2.json()["detail"].lower()


# =========================================================================
# TEST 11: Call /refresh with access token (Expected: 401 Unauthorized)
# =========================================================================
def test_11_refresh_with_access_token(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    access_token = login_resp.json()["access_token"]

    client.cookies.set("refresh_token", access_token)
    response = client.post("/api/auth/refresh")
    assert response.status_code == 401
    assert "refresh token required" in response.json()["detail"].lower()


# =========================================================================
# TEST 12: Logout (Expected: refresh cookie cleared and token revoked)
# =========================================================================
def test_12_logout_clears_cookie(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    refresh_token = login_resp.cookies["refresh_token"]

    client.cookies.set("refresh_token", refresh_token)
    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    assert logout_resp.json()["message"] == "Logged out successfully"


# =========================================================================
# TEST 13: Use revoked refresh token (Expected: 401 Unauthorized)
# =========================================================================
def test_13_use_revoked_refresh_token(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    refresh_token = login_resp.cookies["refresh_token"]

    # Log out to revoke the token
    client.cookies.set("refresh_token", refresh_token)
    client.post("/api/auth/logout")

    # Attempt to refresh using the revoked token
    client.cookies.set("refresh_token", refresh_token)
    response = client.post("/api/auth/refresh")
    assert response.status_code == 401


# =========================================================================
# TEST 14: Access protected endpoint with valid access token (Expected: 200 OK)
# =========================================================================
def test_14_protected_endpoint_valid_token(client):
    client.post(
        "/api/auth/register",
        json={"name": "Vinayak", "email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "vinayak@example.com", "password": "StrongPassword123"},
    )
    access_token = login_resp.json()["access_token"]
    user_id = login_resp.json()["user"]["id"]

    response = client.get(
        "/api/auth/protected",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Authenticated access granted"
    assert str(data["user_id"]) == str(user_id)


# =========================================================================
# TEST 15: Access protected endpoint without token (Expected: 401 Unauthorized)
# =========================================================================
def test_15_protected_endpoint_no_token(client):
    response = client.get("/api/auth/protected")
    assert response.status_code == 401


# =========================================================================
# TEST 16: Expired access token rejected (Expected: 401 Unauthorized)
# =========================================================================
def test_16_expired_access_token(client):
    expired_payload = {
        "sub": "507f1f77bcf86cd799439011",
        "type": "access",
        "jti": "expiredjti",
        "iat": int((datetime.now(timezone.utc) - timedelta(hours=2)).timestamp()),
        "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
    }
    expired_token = jwt.encode(expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()


# =========================================================================
# TEST 17: Inactive user cannot log in or access protected route
# =========================================================================
def test_17_inactive_user(client):
    now = datetime.now(timezone.utc)
    res = mock_db.users.insert_one({
        "name": "Inactive",
        "email": "inactive@example.com",
        "password_hash": hash_password("Password123"),
        "is_active": False,
        "created_at": now,
        "updated_at": now,
    })
    user_id = str(res.inserted_id)

    # Attempt login
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "inactive@example.com", "password": "Password123"},
    )
    assert login_resp.status_code == 401
    assert "inactive" in login_resp.json()["detail"].lower()

    # Generate token and attempt /me
    token = create_access_token(user_id)
    me_resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 401
    assert "inactive" in me_resp.json()["detail"].lower()
