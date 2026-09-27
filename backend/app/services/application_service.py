from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.drive import PlacementDrive, DriveStatus
from app.models.company import Recruiter
from app.models.application import Application, ApplicationStatus
from app.services.drive_service import get_evaluated_drive_status
from app.services.profile_service import calculate_profile_completeness
from app.services.eligibility_service import evaluate_student_eligibility
from app.services.notification_service import create_notification

VALID_TRANSITIONS = {
    ApplicationStatus.APPLIED: {ApplicationStatus.SHORTLISTED, ApplicationStatus.REJECTED},
    ApplicationStatus.SHORTLISTED: {ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED},
    ApplicationStatus.INTERVIEW: {ApplicationStatus.SELECTED, ApplicationStatus.REJECTED},
    ApplicationStatus.SELECTED: set(),
    ApplicationStatus.REJECTED: set(),
}


def submit_application(student_id: int, drive_id: int, db: Session) -> Application:
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Placement Drive with ID {drive_id} not found."
        )

    eval_status = get_evaluated_drive_status(drive)
    if eval_status != DriveStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot apply to drive with status '{eval_status.value}'. Drive must be OPEN."
        )

    now_utc = datetime.now(timezone.utc)
    deadline = drive.application_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)

    if now_utc > deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Application period for this drive has closed."
        )

    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        student = Student(id=student_id, student_code=f"STU{student_id:06d}")
        db.add(student)
        db.commit()
        db.refresh(student)

    _, is_complete, missing_fields = calculate_profile_completeness(student)
    if not is_complete:
        missing_str = ", ".join(missing_fields)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Please complete your profile before applying. Missing fields: [{missing_str}]"
        )

    is_eligible, reasons = evaluate_student_eligibility(student, drive)
    if not is_eligible:
        reasons_str = "; ".join(reasons)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are not eligible for this drive. Reasons: [{reasons_str}]"
        )

    existing = db.query(Application).filter(
        Application.student_id == student_id,
        Application.drive_id == drive_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied for this placement drive."
        )

    new_app = Application(
        student_id=student_id,
        drive_id=drive_id,
        status=ApplicationStatus.APPLIED
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app


def transition_application_status(
    application_id: int,
    target_status: ApplicationStatus,
    current_user: User,
    db: Session
) -> Application:
    app_record = db.query(Application).filter(Application.id == application_id).first()
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found."
        )

    if current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == current_user.id).first()
        if not recruiter or recruiter.company_id != app_record.drive.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. You can only manage candidates for your own company's drives."
            )

    current_status = app_record.status
    if current_status == target_status:
        return app_record

    allowed_next_states = VALID_TRANSITIONS.get(current_status, set())
    if target_status not in allowed_next_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status.value} to {target_status.value}."
        )

    app_record.status = target_status

    # Trigger In-App Notification Events
    company_name = app_record.drive.company.name if (app_record.drive and app_record.drive.company) else "Company"
    job_title = app_record.drive.job_title if app_record.drive else "Job Position"

    if target_status == ApplicationStatus.SHORTLISTED:
        create_notification(
            db=db,
            user_id=app_record.student_id,
            title="Application Shortlisted",
            message=f"Your application for {job_title} at {company_name} has been shortlisted!"
        )
    elif target_status == ApplicationStatus.REJECTED:
        create_notification(
            db=db,
            user_id=app_record.student_id,
            title="Application Status Update",
            message=f"Your application status for {job_title} at {company_name} has been updated to Rejected."
        )

    db.commit()
    db.refresh(app_record)
    return app_record
