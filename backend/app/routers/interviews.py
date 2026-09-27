from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Recruiter
from app.models.drive import PlacementDrive
from app.models.application import Application
from app.models.interview import Interview
from app.schemas.interview import InterviewCreate, InterviewResultUpdate, InterviewResponse
from app.auth.dependencies import RoleChecker
from app.services.interview_service import schedule_interview, submit_interview_result

router = APIRouter(prefix="/api/v1/interviews", tags=["Interview Management"])

recruiter_only = RoleChecker([UserRole.RECRUITER])
all_roles = RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.STUDENT])


def _build_interview_response(interview: Interview) -> InterviewResponse:
    app_rec = interview.application
    student = app_rec.student if app_rec else None
    drive = app_rec.drive if app_rec else None
    company_name = drive.company.name if (drive and drive.company) else "Unknown"

    return InterviewResponse(
        id=interview.id,
        application_id=interview.application_id,
        student_id=app_rec.student_id if app_rec else 0,
        student_name=student.full_name if student else None,
        student_code=student.student_code if student else "",
        job_title=drive.job_title if drive else "",
        company_name=company_name,
        scheduled_time=interview.scheduled_time,
        mode=interview.mode,
        location_or_link=interview.location_or_link,
        result=interview.result,
        feedback=interview.feedback,
        created_at=interview.created_at
    )


@router.post("", response_model=InterviewResponse, status_code=status.HTTP_201_CREATED)
def schedule_candidate_interview(
    schedule_data: InterviewCreate,
    current_user: User = Depends(recruiter_only),
    db: Session = Depends(get_db)
):
    """[RECRUITER] Schedules an interview round for a shortlisted applicant and transitions application to INTERVIEW status."""
    new_interview = schedule_interview(db=db, recruiter_user=current_user, schedule_data=schedule_data)
    return _build_interview_response(new_interview)


@router.get("", response_model=List[InterviewResponse])
def list_interviews(
    current_user: User = Depends(all_roles),
    db: Session = Depends(get_db)
):
    """[ALL ROLES] Lists scheduled interviews scoped by user role and company boundaries."""
    query = db.query(Interview).join(Application).join(PlacementDrive)

    if current_user.role == UserRole.STUDENT:
        query = query.filter(Application.student_id == current_user.id)
    elif current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == current_user.id).first()
        if not recruiter:
            return []
        query = query.filter(PlacementDrive.company_id == recruiter.company_id)

    interviews = query.order_by(Interview.scheduled_time.asc()).all()
    return [_build_interview_response(inv) for inv in interviews]


@router.put("/{interview_id}/result", response_model=InterviewResponse)
def grade_interview(
    interview_id: int,
    result_data: InterviewResultUpdate,
    current_user: User = Depends(recruiter_only),
    db: Session = Depends(get_db)
):
    """[RECRUITER] Submits interview outcome (PASSED/FAILED) and feedback. Automatically rejects failed candidates."""
    updated_interview = submit_interview_result(
        db=db,
        recruiter_user=current_user,
        interview_id=interview_id,
        result_data=result_data
    )
    return _build_interview_response(updated_interview)
