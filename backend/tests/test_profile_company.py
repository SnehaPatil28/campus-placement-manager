import pytest
from app.models.user import User, UserRole
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_users(db_session):
    admin_user = User(id=1, email="admin@test.com", hashed_password=hash_password("admin123"), role=UserRole.ADMIN)
    student_user = User(id=2, email="student@test.com", hashed_password=hash_password("student123"), role=UserRole.STUDENT)
    recruiter_user = User(id=3, email="recruiter@test.com", hashed_password=hash_password("recruiter123"), role=UserRole.RECRUITER)

    db_session.add_all([admin_user, student_user, recruiter_user])
    db_session.commit()


def get_auth_header(user_id: int, role: str) -> dict:
    token = create_access_token({"sub": str(user_id), "role": role})
    return {"Authorization": f"Bearer {token}"}


# --------------------------------------------------------------------------
# Student Profile Tests
# --------------------------------------------------------------------------

def test_get_student_profile_auto_creates_blank(client):
    headers = get_auth_header(2, "STUDENT")
    res = client.get("/api/v1/students/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["student_code"] == "STU000002"
    assert data["is_profile_complete"] is False
    assert data["completeness_percentage"] == 16  # only backlogs default=0 fulfills 1/6 item (~16%)
    assert "full_name" in data["missing_fields"]
    assert "branch" in data["missing_fields"]


def test_update_student_profile_to_100_percent(client):
    headers = get_auth_header(2, "STUDENT")

    update_payload = {
        "full_name": "Aarav Sharma",
        "phone": "+919876543210",
        "branch": "AIML",
        "graduation_year": 2027,
        "cgpa": 8.5,
        "backlogs": 0,
        "resume_url": "https://example.com/resume.pdf",
        "skills": ["Python", "SQL", "FastAPI"]
    }

    res = client.put("/api/v1/students/me", json=update_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()

    assert data["full_name"] == "Aarav Sharma"
    assert data["branch"] == "AIML"
    assert data["cgpa"] == 8.5
    assert set(data["skills"]) == {"Python", "SQL", "FastAPI"}
    assert data["completeness_percentage"] == 100
    assert data["is_profile_complete"] is True
    assert len(data["missing_fields"]) == 0


def test_student_profile_skill_tag_sync(client):
    headers = get_auth_header(2, "STUDENT")

    client.put("/api/v1/students/me", json={"skills": ["Python", "SQL"]}, headers=headers)

    res = client.put("/api/v1/students/me", json={"skills": ["React", "TypeScript"]}, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert set(data["skills"]) == {"React", "TypeScript"}


# --------------------------------------------------------------------------
# Company Management Tests
# --------------------------------------------------------------------------

def test_admin_create_company_success(client):
    headers = get_auth_header(1, "ADMIN")
    payload = {
        "name": "Thinqloud Systems",
        "industry": "IT Services & Consulting",
        "location": "Pune, India",
        "is_active": True
    }
    res = client.post("/api/v1/companies", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Thinqloud Systems"
    assert data["id"] is not None


def test_admin_create_duplicate_company_fails(client):
    headers = get_auth_header(1, "ADMIN")
    payload = {"name": "Tech Corp", "industry": "Tech", "location": "Bangalore"}

    res1 = client.post("/api/v1/companies", json=payload, headers=headers)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/companies", json=payload, headers=headers)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


def test_student_cannot_create_company(client):
    headers = get_auth_header(2, "STUDENT")
    payload = {"name": "Hacker Corp", "industry": "Tech", "location": "Remote"}

    res = client.post("/api/v1/companies", json=payload, headers=headers)
    assert res.status_code == 403
    assert "Operation not permitted" in res.json()["detail"]


def test_list_and_update_company(client):
    admin_headers = get_auth_header(1, "ADMIN")
    recruiter_headers = get_auth_header(3, "RECRUITER")

    c_res = client.post("/api/v1/companies", json={"name": "Acme Inc", "industry": "Finance", "location": "Mumbai"}, headers=admin_headers)
    company_id = c_res.json()["id"]

    list_res = client.get("/api/v1/companies", headers=recruiter_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    update_res = client.put(f"/api/v1/companies/{company_id}", json={"location": "Navi Mumbai", "is_active": False}, headers=admin_headers)
    assert update_res.status_code == 200
    assert update_res.json()["location"] == "Navi Mumbai"
    assert update_res.json()["is_active"] is False
