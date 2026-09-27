from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.company import Recruiter
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview, InterviewMode, InterviewResult
from app.schemas.interview import InterviewCreate, InterviewResultUpdate
from app.services.notification_service import create_notification


def schedule_interview(db: Session, recruiter_user: User, schedule_data: InterviewCreate) -> Interview:
    app_record = db.query(Application).filter(Application.id == schedule_data.application_id).first()
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {schedule_data.application_id} not found."
        )

    if recruiter_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == recruiter_user.id).first()
        if not recruiter or recruiter.company_id != app_record.drive.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. You can only schedule interviews for your company's drives."
            )

    if app_record.status != ApplicationStatus.SHORTLISTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only SHORTLISTED candidates can be scheduled for interviews. Candidate is currently '{app_record.status.value}'."
        )

    new_interview = Interview(
        application_id=app_record.id,
        scheduled_time=schedule_data.scheduled_time,
        mode=schedule_data.mode,
        location_or_link=schedule_data.location_or_link,
        result=InterviewResult.PENDING,
        feedback=None
    )
    app_record.status = ApplicationStatus.INTERVIEW

    # Trigger Interview Scheduled Notification
    job_title = app_record.drive.job_title if app_record.drive else "Job Position"
    sched_str = schedule_data.scheduled_time.strftime("%Y-%m-%d %H:%M")
    create_notification(
        db=db,
        user_id=app_record.student_id,
        title="Interview Scheduled",
        message=f"Interview scheduled for {job_title} on {sched_str} ({schedule_data.mode.value}). Link/Location: {schedule_data.location_or_link}"
    )

    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    return new_interview


def submit_interview_result(db: Session, recruiter_user: User, interview_id: int, result_data: InterviewResultUpdate) -> Interview:
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Interview with ID {interview_id} not found."
        )

    app_record = interview.application

    if recruiter_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == recruiter_user.id).first()
        if not recruiter or recruiter.company_id != app_record.drive.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. You can only grade interviews for your company's drives."
            )

    interview.result = result_data.result
    interview.feedback = result_data.feedback

    if result_data.result == InterviewResult.FAILED:
        app_record.status = ApplicationStatus.REJECTED
        company_name = app_record.drive.company.name if (app_record.drive and app_record.drive.company) else "Company"
        job_title = app_record.drive.job_title if app_record.drive else "Job Position"
        create_notification(
            db=db,
            user_id=app_record.student_id,
            title="Application Status Update",
            message=f"Your application status for {job_title} at {company_name} has been updated to Rejected."
        )

    db.commit()
    db.refresh(interview)
    return interview
