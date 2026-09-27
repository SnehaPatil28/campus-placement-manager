from datetime import datetime, timedelta, timezone
import pytest
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.student import Student, Skill
from app.models.drive import PlacementDrive, DriveStatus
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_data(db_session):
    admin_user = User(id=1, email="admin@test.com", hashed_password=hash_password("admin123"), role=UserRole.ADMIN)
    student_user = User(id=2, email="student@test.com", hashed_password=hash_password("student123"), role=UserRole.STUDENT)
    recruiter_user = User(id=3, email="recruiter@test.com", hashed_password=hash_password("recruiter123"), role=UserRole.RECRUITER)

    company = Company(id=10, name="ABC Technologies", industry="Software", location="Pune")

    db_session.add_all([admin_user, student_user, recruiter_user, company])
    db_session.commit()


def get_auth_header(user_id: int, role: str) -> dict:
    token = create_access_token({"sub": str(user_id), "role": role})
    return {"Authorization": f"Bearer {token}"}


def test_admin_create_drive(client):
    headers = get_auth_header(1, "ADMIN")
    deadline = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

    payload = {
        "company_id": 10,
        "job_title": "Software Engineer — AIML",
        "job_description": "Building scalable ML models",
        "package_lpa": 8.5,
        "location": "Pune",
        "min_cgpa": 7.5,
        "max_backlogs": 0,
        "graduation_year": 2027,
        "allowed_branches": ["CSE", "IT", "AIML"],
        "required_skills": ["Python", "SQL"],
        "application_deadline": deadline,
        "status": "OPEN"
    }

    res = client.post("/api/v1/drives", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["job_title"] == "Software Engineer — AIML"
    assert data["company_name"] == "ABC Technologies"
    assert data["status"] == "OPEN"
    assert set(data["allowed_branches"]) == {"CSE", "IT", "AIML"}


def test_student_eligibility_success(client, db_session):
    # Setup eligible student (CGPA: 8.2, AIML, 2027, 0 backlogs, Python, SQL)
    student = Student(
        id=2,
        student_code="STU000002",
        full_name="Eligible Candidate",
        branch="AIML",
        graduation_year=2027,
        cgpa=8.2,
        backlogs=0
    )
    db_session.add(student)
    db_session.flush()

    s1 = Skill(student_id=2, skill_name="Python")
    s2 = Skill(student_id=2, skill_name="SQL")
    db_session.add_all([s1, s2])

    # Setup drive (min_cgpa: 7.5, AIML, 2027, max_backlogs: 0, required_skills: Python)
    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    drive = PlacementDrive(
        id=100,
        company_id=10,
        job_title="Data Scientist",
        job_description="Desc",
        package_lpa=10.0,
        location="Remote",
        min_cgpa=7.5,
        max_backlogs=0,
        graduation_year=2027,
        allowed_branches="CSE,IT,AIML",
        required_skills="Python",
        application_deadline=deadline,
        status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.commit()

    student_headers = get_auth_header(2, "STUDENT")
    res = client.get("/api/v1/drives/100/eligibility", headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_eligible"] is True
    assert len(data["reasons"]) == 0


def test_student_eligibility_failures(client, db_session):
    # Setup student failing CGPA (6.5), Branch (Civil), Backlogs (2), Missing Docker skill
    student = Student(
        id=2,
        student_code="STU000002",
        full_name="Ineligible Candidate",
        branch="Civil",
        graduation_year=2027,
        cgpa=6.5,
        backlogs=2
    )
    db_session.add(student)
    db_session.flush()
    db_session.add(Skill(student_id=2, skill_name="Python"))

    # Drive requiring min CGPA 7.5, CSE/IT, max backlogs 0, required skills: Python, Docker
    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    drive = PlacementDrive(
        id=101,
        company_id=10,
        job_title="DevOps Engineer",
        job_description="Desc",
        package_lpa=9.0,
        location="Bangalore",
        min_cgpa=7.5,
        max_backlogs=0,
        graduation_year=2027,
        allowed_branches="CSE,IT",
        required_skills="Python,Docker",
        application_deadline=deadline,
        status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.commit()

    student_headers = get_auth_header(2, "STUDENT")
    res = client.get("/api/v1/drives/101/eligibility", headers=student_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["is_eligible"] is False
    assert len(data["reasons"]) >= 4  # CGPA, Backlogs, Branch, Docker missing


def test_dynamic_status_computation_closed_on_expired_deadline(client, db_session):
    # Create drive with expired deadline
    expired_deadline = datetime.now(timezone.utc) - timedelta(days=1)
    drive = PlacementDrive(
        id=102,
        company_id=10,
        job_title="Old Drive",
        job_description="Desc",
        package_lpa=6.0,
        location="Pune",
        min_cgpa=6.0,
        max_backlogs=1,
        graduation_year=2027,
        allowed_branches="CSE",
        required_skills="Java",
        application_deadline=expired_deadline,
        status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.commit()

    headers = get_auth_header(1, "ADMIN")
    res = client.get("/api/v1/drives/102", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "CLOSED"  # Computed automatically as CLOSED
