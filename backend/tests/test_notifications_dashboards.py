import pytest
from datetime import datetime, timedelta, timezone
from app.models.user import User, UserRole
from app.models.company import Company, Recruiter
from app.models.student import Student, Skill
from app.models.drive import PlacementDrive, DriveStatus
from app.models.application import Application, ApplicationStatus
from app.auth.password import hash_password
from app.auth.jwt import create_access_token


def get_auth_header(user_id: int, role: str) -> dict:
    """Helper to generate JWT bearer header for testing."""
    token = create_access_token({"sub": str(user_id), "role": role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def seed_module6_data(db_session):
    """Seed base users and database entities for Module 6 tests."""
    admin_user = User(id=1, email="admin_m6@test.com", hashed_password=hash_password("admin123"), role=UserRole.ADMIN)
    student_user = User(id=2, email="student_m6@test.com", hashed_password=hash_password("pass123"), role=UserRole.STUDENT)
    recruiter_user = User(id=3, email="recruiter_m6@test.com", hashed_password=hash_password("pass123"), role=UserRole.RECRUITER)

    company = Company(id=1, name="Tech Corp", industry="IT", location="Pune")
    recruiter = Recruiter(id=3, company_id=1, full_name="Recruiter M6")

    db_session.add_all([admin_user, student_user, recruiter_user, company, recruiter])
    db_session.commit()


def setup_drive_and_application(client, db_session):
    """Helper to set up placement drive, student profile, and application."""
    # Student profile setup
    stu = Student(id=2, student_code="STU000002", full_name="Test Student", branch="CSE", graduation_year=2026, cgpa=8.5, backlogs=0, resume_url="https://example.com/resume.pdf")
    db_session.add(stu)
    db_session.flush()
    db_session.add_all([Skill(student_id=2, skill_name="Python"), Skill(student_id=2, skill_name="SQL")])

    # Drive setup
    deadline = datetime.now(timezone.utc) + timedelta(days=5)
    drive = PlacementDrive(
        id=1, company_id=1, job_title="Software Engineer", job_description="Backend role",
        package_lpa=12.0, location="Pune", min_cgpa=7.0, max_backlogs=0,
        graduation_year=2026, allowed_branches="CSE,IT", required_skills="Python,SQL",
        application_deadline=deadline, status=DriveStatus.OPEN
    )
    db_session.add(drive)
    db_session.commit()

    stu_headers = get_auth_header(2, "STUDENT")
    rec_headers = get_auth_header(3, "RECRUITER")
    admin_headers = get_auth_header(1, "ADMIN")

    # Application submission
    app_res = client.post("/api/v1/applications", json={"drive_id": 1}, headers=stu_headers)
    app_id = app_res.json()["id"]

    return {
        "admin_headers": admin_headers,
        "rec_headers": rec_headers,
        "stu_headers": stu_headers,
        "app_id": app_id,
    }


def test_notification_triggers_on_workflow(client, db_session):
    """Test automated notification generation on Shortlist, Interview, Offer, and Reject."""
    setup_data = setup_drive_and_application(client, db_session)
    app_id = setup_data["app_id"]
    rec_headers = setup_data["rec_headers"]
    stu_headers = setup_data["stu_headers"]

    # 1. Shortlist -> Notification 1
    shortlist_res = client.put(f"/api/v1/applications/{app_id}/status", json={"target_status": "SHORTLISTED"}, headers=rec_headers)
    assert shortlist_res.status_code == 200

    notif_res = client.get("/api/v1/notifications", headers=stu_headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()
    assert len(notifs) == 1
    assert notifs[0]["title"] == "Application Shortlisted"
    assert "shortlisted" in notifs[0]["message"]
    assert notifs[0]["is_read"] is False

    # 2. Schedule Interview -> Notification 2
    sched_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    int_res = client.post("/api/v1/interviews", json={
        "application_id": app_id,
        "scheduled_time": sched_time,
        "mode": "ONLINE",
        "location_or_link": "https://meet.google.com/abc-defg-hij"
    }, headers=rec_headers)
    assert int_res.status_code == 201
    int_id = int_res.json()["id"]

    notif_res2 = client.get("/api/v1/notifications", headers=stu_headers)
    notifs2 = notif_res2.json()
    assert len(notifs2) == 2
    assert notifs2[0]["title"] == "Interview Scheduled"

    # Pass Interview
    client.put(f"/api/v1/interviews/{int_id}/result", json={
        "result": "PASSED",
        "feedback": "Great technical skills"
    }, headers=rec_headers)

    # 3. Create Offer -> Notification 3
    offer_res = client.post("/api/v1/offers", json={
        "application_id": app_id,
        "package_offered": 14.5,
        "joining_date": "2026-07-01"
    }, headers=rec_headers)
    assert offer_res.status_code == 201

    notif_res3 = client.get("/api/v1/notifications", headers=stu_headers)
    notifs3 = notif_res3.json()
    assert len(notifs3) == 3
    assert notifs3[0]["title"] == "Congratulations! Offer Received"
    assert "14.5 LPA" in notifs3[0]["message"]


def test_notification_read_endpoints(client, db_session):
    """Test unread count, marking notification as read, and mark-all-read."""
    setup_data = setup_drive_and_application(client, db_session)
    app_id = setup_data["app_id"]
    rec_headers = setup_data["rec_headers"]
    stu_headers = setup_data["stu_headers"]

    # Shortlist to trigger notification
    client.put(f"/api/v1/applications/{app_id}/status", json={"target_status": "SHORTLISTED"}, headers=rec_headers)

    # Check unread count == 1
    unread_res = client.get("/api/v1/notifications/unread-count", headers=stu_headers)
    assert unread_res.status_code == 200
    assert unread_res.json()["unread_count"] == 1

    # Get notification ID
    notifs = client.get("/api/v1/notifications", headers=stu_headers).json()
    notif_id = notifs[0]["id"]

    # Mark single notification as read
    read_res = client.put(f"/api/v1/notifications/{notif_id}/read", headers=stu_headers)
    assert read_res.status_code == 200
    assert read_res.json()["is_read"] is True

    # Check unread count == 0
    unread_res2 = client.get("/api/v1/notifications/unread-count", headers=stu_headers)
    assert unread_res2.json()["unread_count"] == 0

    # Trigger second notification (reject application)
    client.put(f"/api/v1/applications/{app_id}/status", json={"target_status": "REJECTED"}, headers=rec_headers)

    assert client.get("/api/v1/notifications/unread-count", headers=stu_headers).json()["unread_count"] == 1

    # Mark all read
    read_all_res = client.put("/api/v1/notifications/read-all", headers=stu_headers)
    assert read_all_res.status_code == 200
    assert read_all_res.json()["updated_count"] == 1

    assert client.get("/api/v1/notifications/unread-count", headers=stu_headers).json()["unread_count"] == 0


def test_student_dashboard_endpoint(client, db_session):
    """Test Student Dashboard API returns accurate metrics and activity feed."""
    setup_data = setup_drive_and_application(client, db_session)
    stu_headers = setup_data["stu_headers"]

    dash_res = client.get("/api/v1/dashboards/student", headers=stu_headers)
    assert dash_res.status_code == 200
    data = dash_res.json()

    assert data["profile_completion_percentage"] == 100.0
    assert data["is_profile_complete"] is True
    assert data["eligible_drives_count"] == 1
    assert data["active_applications_count"] == 1
    assert len(data["recent_applications"]) == 1
    assert data["recent_applications"][0]["job_title"] == "Software Engineer"


def test_recruiter_dashboard_endpoint(client, db_session):
    """Test Recruiter Dashboard API returns company drive pipeline breakdown."""
    setup_data = setup_drive_and_application(client, db_session)
    rec_headers = setup_data["rec_headers"]

    dash_res = client.get("/api/v1/dashboards/recruiter", headers=rec_headers)
    assert dash_res.status_code == 200
    data = dash_res.json()

    assert data["company_name"] == "Tech Corp"
    assert data["active_drives_count"] == 1
    assert data["total_applicants"] == 1
    assert data["pipeline_breakdown"]["APPLIED"] == 1


def test_admin_dashboard_endpoint(client, db_session):
    """Test Admin Dashboard API returns system-wide metrics and branch breakdown."""
    setup_data = setup_drive_and_application(client, db_session)
    admin_headers = setup_data["admin_headers"]
    rec_headers = setup_data["rec_headers"]
    app_id = setup_data["app_id"]

    # Pass interview and issue offer to make student PLACED
    client.put(f"/api/v1/applications/{app_id}/status", json={"target_status": "SHORTLISTED"}, headers=rec_headers)
    sched_time = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    int_res = client.post("/api/v1/interviews", json={
        "application_id": app_id,
        "scheduled_time": sched_time,
        "mode": "ONLINE",
        "location_or_link": "Room 101"
    }, headers=rec_headers)
    int_id = int_res.json()["id"]
    client.put(f"/api/v1/interviews/{int_id}/result", json={"result": "PASSED"}, headers=rec_headers)
    client.post("/api/v1/offers", json={"application_id": app_id, "package_offered": 10.0, "joining_date": "2026-07-01"}, headers=rec_headers)

    dash_res = client.get("/api/v1/dashboards/admin", headers=admin_headers)
    assert dash_res.status_code == 200
    data = dash_res.json()

    assert data["total_registered_students"] >= 1
    assert data["total_partner_companies"] == 1
    assert data["active_drives_count"] == 1
    assert data["total_applications_submitted"] == 1
    assert data["placed_students_count"] == 1
    assert data["placement_percentage"] > 0.0
    assert len(data["department_breakdown"]) >= 1
    cse_branch = next(b for b in data["department_breakdown"] if b["branch"] == "CSE")
    assert cse_branch["total_students"] == 1
    assert cse_branch["placed_students"] == 1
    assert cse_branch["placement_percentage"] == 100.0


def test_role_dashboard_authorization_guards(client):
    """Test RBAC on dashboard endpoints (Student cannot access Admin/Recruiter dashboards)."""
    stu_headers = get_auth_header(2, "STUDENT")

    rec_res = client.get("/api/v1/dashboards/recruiter", headers=stu_headers)
    assert rec_res.status_code == 403

    admin_res = client.get("/api/v1/dashboards/admin", headers=stu_headers)
    assert admin_res.status_code == 403
