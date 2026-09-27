import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_student_success(client):
    payload = {
        "email": "student@college.edu",
        "password": "SecurePassword123!"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "student@college.edu"
    assert data["role"] == "STUDENT"
    assert data["is_active"] is True
    assert "id" in data


def test_register_student_duplicate_email(client):
    payload = {
        "email": "duplicate@college.edu",
        "password": "Password123!"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_login_success_and_get_me(client):
    reg_payload = {
        "email": "login_test@college.edu",
        "password": "MyPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_data = {
        "username": "login_test@college.edu",
        "password": "MyPassword123"
    }
    res = client.post("/api/v1/auth/login", data=login_data)
    assert res.status_code == 200
    token_response = res.json()
    assert "access_token" in token_response
    assert token_response["token_type"] == "bearer"
    assert token_response["role"] == "STUDENT"

    token = token_response["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == "login_test@college.edu"
    assert me_data["role"] == "STUDENT"


def test_login_invalid_password(client):
    reg_payload = {
        "email": "wrongpass@college.edu",
        "password": "CorrectPassword123"
    }
    client.post("/api/v1/auth/register", json=reg_payload)

    login_data = {
        "username": "wrongpass@college.edu",
        "password": "WrongPassword123"
    }
    res = client.post("/api/v1/auth/login", data=login_data)
    assert res.status_code == 401
    assert "Incorrect email or password" in res.json()["detail"]


def test_unauthorized_access_to_me(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 401
