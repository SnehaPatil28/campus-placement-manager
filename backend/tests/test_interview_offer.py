from datetime import datetime, timedelta, timezone, date
import pytest
from app.models.user import User, UserRole
from app.models.company import Company, Recruiter
from app.models.student import Student, Skill
from app.models.drive import PlacementDrive, DriveStatus
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview, InterviewResult, InterviewMode
from app.models.offer import Offer, OfferStatus
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


@pytest.fixture(autouse=True)
def seed_data(db_session):
    admin_user = User(id=1, email="admin@test.com", hashed_password=hash_password("admin123"), role=UserRole.ADMIN)
    student_user = User(id=2, email="student@test.com", hashed_password=hash_password("pass123"), role=UserRole.STUDENT)
    recruiter_user = User(id=3, email="recruiter@test.com", hashed_password=hash_password("pass123"), role=UserRole.RECRUITER)

    company = Company(id=10, name="Thinqloud Systems", industry="IT", location="Pune")
    recruiter = Recruiter(id=3, company_id=10, full_name="Recruiter Lead")

    student = Student(id=2, student_code="STU000002", full_name="Candidate A", branch="AIML", graduation_year=2027, cgpa=8.5, backlogs=0)

    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    drive = PlacementDrive(
        id=100, company_id=10, job_title="Software Engineer", job_description="Desc",
        package_lpa=8.5, location="Pune", min_cgpa=7.5, max_backlogs=0,
        graduation_year=2027, allowed_branches="AIML", required_skills="Python",
        application_deadline=deadline, status=DriveStatus.OPEN
    )

    db_session.add_all([admin_user, student_user, recruiter_user, company, recruiter, student, drive])
    db_session.commit()


def get_auth_header(user_id: int, role: str) -> dict:
    token = create_access_token({"sub": str(user_id), "role": role})
    return {"Authorization": f"Bearer {token}"}


def test_schedule_interview_for_shortlisted_candidate(client, db_session):
    # Application in SHORTLISTED status
    app_rec = Application(id=50, student_id=2, drive_id=100, status=ApplicationStatus.SHORTLISTED)
    db_session.add(app_rec)
    db_session.commit()

    rec_headers = get_auth_header(3, "RECRUITER")
    sched_time = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    payload = {
        "application_id": 50,
        "scheduled_time": sched_time,
        "mode": "ONLINE",
        "location_or_link": "https://meet.google.com/abc-defg-hij"
    }

    res = client.post("/api/v1/interviews", json=payload, headers=rec_headers)
    assert res.status_code == 201
    data = res.json()
    assert data["application_id"] == 50
    assert data["result"] == "PENDING"
    assert data["job_title"] == "Software Engineer"

    # Application state automatically transitioned to INTERVIEW
    db_session.refresh(app_rec)
    assert app_rec.status == ApplicationStatus.INTERVIEW


def test_schedule_interview_for_non_shortlisted_candidate_fails(client, db_session):
    # Application in APPLIED status (not shortlisted yet)
    app_rec = Application(id=51, student_id=2, drive_id=100, status=ApplicationStatus.APPLIED)
    db_session.add(app_rec)
    db_session.commit()

    rec_headers = get_auth_header(3, "RECRUITER")
    payload = {
        "application_id": 51,
        "scheduled_time": (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        "mode": "ONLINE",
        "location_or_link": "https://meet.google.com/abc-defg-hij"
    }

    res = client.post("/api/v1/interviews", json=payload, headers=rec_headers)
    assert res.status_code == 400
    assert "Only SHORTLISTED candidates can be scheduled" in res.json()["detail"]


def test_grade_interview_passed_and_issue_offer_and_accept(client, db_session):
    # 1. Setup application in INTERVIEW status with scheduled interview
    app_rec = Application(id=52, student_id=2, drive_id=100, status=ApplicationStatus.INTERVIEW)
    db_session.add(app_rec)
    db_session.flush()

    inv = Interview(id=20, application_id=52, scheduled_time=datetime.now(timezone.utc), mode=InterviewMode.ONLINE, location_or_link="Link", result=InterviewResult.PENDING)
    db_session.add(inv)
    db_session.commit()

    rec_headers = get_auth_header(3, "RECRUITER")
    stu_headers = get_auth_header(2, "STUDENT")

    # 2. Grade interview as PASSED
    grade_res = client.put("/api/v1/interviews/20/result", json={"result": "PASSED", "feedback": "Excellent technical performance"}, headers=rec_headers)
    assert grade_res.status_code == 200
    assert grade_res.json()["result"] == "PASSED"

    # 3. Recruiter issues formal offer
    offer_payload = {
        "application_id": 52,
        "package_offered": 8.5,
        "joining_date": str(date.today() + timedelta(days=60))
    }
    offer_res = client.post("/api/v1/offers", json=offer_payload, headers=rec_headers)
    assert offer_res.status_code == 201
    offer_data = offer_res.json()
    assert offer_data["status"] == "OFFERED"
    assert offer_data["package_offered"] == 8.5
    offer_id = offer_data["id"]

    # Application state automatically transitioned to SELECTED
    db_session.refresh(app_rec)
    assert app_rec.status == ApplicationStatus.SELECTED

    # 4. Student views and accepts offer
    accept_res = client.put(f"/api/v1/offers/{offer_id}/status", json={"status": "ACCEPTED"}, headers=stu_headers)
    assert accept_res.status_code == 200
    assert accept_res.json()["status"] == "ACCEPTED"


def test_failed_interview_automatically_rejects_candidate(client, db_session):
    app_rec = Application(id=53, student_id=2, drive_id=100, status=ApplicationStatus.INTERVIEW)
    db_session.add(app_rec)
    db_session.flush()

    inv = Interview(id=21, application_id=53, scheduled_time=datetime.now(timezone.utc), mode=InterviewMode.ONLINE, location_or_link="Link", result=InterviewResult.PENDING)
    db_session.add(inv)
    db_session.commit()

    rec_headers = get_auth_header(3, "RECRUITER")

    # Grade as FAILED
    res = client.put("/api/v1/interviews/21/result", json={"result": "FAILED", "feedback": "Lacks required SQL skills"}, headers=rec_headers)
    assert res.status_code == 200
    assert res.json()["result"] == "FAILED"

    # Application state auto-transitions to REJECTED
    db_session.refresh(app_rec)
    assert app_rec.status == ApplicationStatus.REJECTED

    # Attempting to issue offer to failed candidate fails
    offer_payload = {
        "application_id": 53,
        "package_offered": 8.5,
        "joining_date": str(date.today() + timedelta(days=60))
    }
    offer_fail_res = client.post("/api/v1/offers", json=offer_payload, headers=rec_headers)
    assert offer_fail_res.status_code == 400
    assert "PASSED an interview" in offer_fail_res.json()["detail"]
