from datetime import datetime, timedelta, timezone
import pytest
from app.models.user import User, UserRole
from app.models.company import Company, Recruiter
from app.models.student import Student, Skill
from app.models.drive import PlacementDrive, DriveStatus
from app.models.application import Application, ApplicationStatus
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_data(db_session):
    # Create Admin (1), Eligible Student A (2), Incomplete Student B (3), Recruiter A (4), Recruiter B (5)
    admin_user = User(id=1, email="admin@test.com", hashed_password=hash_password("admin123"), role=UserRole.ADMIN)
    student_a = User(id=2, email="student_a@test.com", hashed_password=hash_password("pass123"), role=UserRole.STUDENT)
    student_b = User(id=3, email="student_b@test.com", hashed_password=hash_password("pass123"), role=UserRole.STUDENT)
    recruiter_a_user = User(id=4, email="recruiter_a@test.com", hashed_password=hash_password("pass123"), role=UserRole.RECRUITER)
    recruiter_b_user = User(id=5, email="recruiter_b@test.com", hashed_password=hash_password("pass123"), role=UserRole.RECRUITER)

    c1 = Company(id=10, name="Thinqloud Systems", industry="IT", location="Pune")
    c2 = Company(id=20, name="Global Tech", industry="Tech", location="Bangalore")

    rec_a = Recruiter(id=4, company_id=10, full_name="Recruiter A")
    rec_b = Recruiter(id=5, company_id=20, full_name="Recruiter B")

    db_session.add_all([
        admin_user, student_a, student_b, recruiter_a_user, recruiter_b_user,
        c1, c2, rec_a, rec_b
    ])
    db_session.commit()


def get_auth_header(user_id: int, role: str) -> dict:
    token = create_access_token({"sub": str(user_id), "role": role})
    return {"Authorization": f"Bearer {token}"}


def test_eligible_student_applies_successfully(client, db_session):
    # Setup complete eligible student A
    stu_a = Student(id=2, student_code="STU000002", full_name="Student A", branch="AIML", graduation_year=2027, cgpa=8.5, backlogs=0)
    db_session.add(stu_a)
    db_session.flush()
    db_session.add(Skill(student_id=2, skill_name="Python"))

    # Setup open drive for Company 10
    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    drive = PlacementDrive(
        id=100, company_id=10, job_title="AIML Engineer", job_description="Desc",
        package_lpa=8.0, location="Pune", min_cgpa=7.0, max_backlogs=0,
        graduation_year=2027, allowed_branches="AIML,CSE", required_skills="Python",
        application_deadline=deadline, status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.commit()

    headers = get_auth_header(2, "STUDENT")
    res = client.post("/api/v1/applications", json={"drive_id": 100}, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "APPLIED"
    assert data["drive_id"] == 100
    assert data["company_name"] == "Thinqloud Systems"


def test_incomplete_profile_cannot_apply(client, db_session):
    # Student B has blank incomplete profile
    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    drive = PlacementDrive(
        id=101, company_id=10, job_title="Dev", job_description="Desc",
        package_lpa=6.0, location="Pune", min_cgpa=6.0, max_backlogs=1,
        graduation_year=2027, allowed_branches="CSE", required_skills="Python",
        application_deadline=deadline, status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.commit()

    headers = get_auth_header(3, "STUDENT")
    res = client.post("/api/v1/applications", json={"drive_id": 101}, headers=headers)
    assert res.status_code == 422
    assert "Please complete your profile before applying" in res.json()["detail"]


def test_duplicate_application_fails(client, db_session):
    stu_a = Student(id=2, student_code="STU000002", full_name="Student A", branch="AIML", graduation_year=2027, cgpa=8.5, backlogs=0)
    db_session.add(stu_a)
    db_session.flush()
    db_session.add(Skill(student_id=2, skill_name="Python"))

    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    drive = PlacementDrive(
        id=102, company_id=10, job_title="Dev", job_description="Desc",
        package_lpa=6.0, location="Pune", min_cgpa=6.0, max_backlogs=1,
        graduation_year=2027, allowed_branches="AIML", required_skills="Python",
        application_deadline=deadline, status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.commit()

    headers = get_auth_header(2, "STUDENT")
    # First application
    res1 = client.post("/api/v1/applications", json={"drive_id": 102}, headers=headers)
    assert res1.status_code == 201

    # Duplicate application
    res2 = client.post("/api/v1/applications", json={"drive_id": 102}, headers=headers)
    assert res2.status_code == 409
    assert "already applied" in res2.json()["detail"]


def test_state_machine_valid_transition_and_scoping(client, db_session):
    stu_a = Student(id=2, student_code="STU000002", full_name="Student A", branch="AIML", graduation_year=2027, cgpa=8.5, backlogs=0)
    db_session.add(stu_a)
    db_session.flush()

    drive = PlacementDrive(
        id=103, company_id=10, job_title="Dev", job_description="Desc",
        package_lpa=6.0, location="Pune", min_cgpa=6.0, max_backlogs=1,
        graduation_year=2027, allowed_branches="AIML", required_skills="Python",
        application_deadline=datetime.now(timezone.utc) + timedelta(days=5), status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.flush()

    app_rec = Application(id=50, student_id=2, drive_id=103, status=ApplicationStatus.APPLIED)
    db_session.add(app_rec)
    db_session.commit()

    rec_a_headers = get_auth_header(4, "RECRUITER")  # Recruiter for Company 10
    rec_b_headers = get_auth_header(5, "RECRUITER")  # Recruiter for Company 20

    # Recruiter B attempts to update Company 10 application -> 403 Forbidden
    res_b = client.put("/api/v1/applications/50/status", json={"target_status": "SHORTLISTED"}, headers=rec_b_headers)
    assert res_b.status_code == 403

    # Recruiter A shortlists Candidate -> 200 OK
    res_a = client.put("/api/v1/applications/50/status", json={"target_status": "SHORTLISTED"}, headers=rec_a_headers)
    assert res_a.status_code == 200
    assert res_a.json()["status"] == "SHORTLISTED"


def test_state_machine_invalid_direct_jump(client, db_session):
    stu_a = Student(id=2, student_code="STU000002", full_name="Student A", branch="AIML", graduation_year=2027, cgpa=8.5, backlogs=0)
    db_session.add(stu_a)
    db_session.flush()

    drive = PlacementDrive(
        id=104, company_id=10, job_title="Dev", job_description="Desc",
        package_lpa=6.0, location="Pune", min_cgpa=6.0, max_backlogs=1,
        graduation_year=2027, allowed_branches="AIML", required_skills="Python",
        application_deadline=datetime.now(timezone.utc) + timedelta(days=5), status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.flush()

    app_rec = Application(id=51, student_id=2, drive_id=104, status=ApplicationStatus.APPLIED)
    db_session.add(app_rec)
    db_session.commit()

    rec_a_headers = get_auth_header(4, "RECRUITER")

    # Invalid jump: APPLIED -> SELECTED directly
    res = client.put("/api/v1/applications/51/status", json={"target_status": "SELECTED"}, headers=rec_a_headers)
    assert res.status_code == 400
    assert "Invalid status transition" in res.json()["detail"]
