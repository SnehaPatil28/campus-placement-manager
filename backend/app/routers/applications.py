from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Recruiter
from app.models.drive import PlacementDrive
from app.models.application import Application, ApplicationStatus
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate, ApplicationResponse
from app.auth.dependencies import RoleChecker
from app.services.application_service import submit_application, transition_application_status

router = APIRouter(prefix="/api/v1/applications", tags=["Application Management"])

student_only = RoleChecker([UserRole.STUDENT])
admin_or_recruiter = RoleChecker([UserRole.ADMIN, UserRole.RECRUITER])
all_roles = RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.STUDENT])


def _build_application_response(app_rec: Application) -> ApplicationResponse:
    student = app_rec.student
    drive = app_rec.drive
    company_name = drive.company.name if (drive and drive.company) else "Unknown"

    return ApplicationResponse(
        id=app_rec.id,
        student_id=app_rec.student_id,
        student_name=student.full_name if student else None,
        student_code=student.student_code if student else f"STU{app_rec.student_id:06d}",
        student_branch=student.branch if student else None,
        student_cgpa=student.cgpa if student else None,
        drive_id=app_rec.drive_id,
        job_title=drive.job_title if drive else "",
        company_name=company_name,
        status=app_rec.status,
        applied_at=app_rec.applied_at
    )


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_for_placement_drive(
    app_in: ApplicationCreate,
    current_user: User = Depends(student_only),
    db: Session = Depends(get_db)
):
    """[STUDENT] Submits an application for a placement drive following the Pre-Application Guard Chain."""
    new_app = submit_application(student_id=current_user.id, drive_id=app_in.drive_id, db=db)
    return _build_application_response(new_app)


@router.get("", response_model=List[ApplicationResponse])
def list_applications(
    drive_id: Optional[int] = None,
    status_filter: Optional[ApplicationStatus] = None,
    current_user: User = Depends(all_roles),
    db: Session = Depends(get_db)
):
    """[ALL ROLES] Lists applications scoped to current user's role and company permissions."""
    query = db.query(Application).join(PlacementDrive)

    # Role Scoping
    if current_user.role == UserRole.STUDENT:
        query = query.filter(Application.student_id == current_user.id)
    elif current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == current_user.id).first()
        if not recruiter:
            return []
        query = query.filter(PlacementDrive.company_id == recruiter.company_id)

    # Optional Query Filters
    if drive_id is not None:
        query = query.filter(Application.drive_id == drive_id)

    if status_filter is not None:
        query = query.filter(Application.status == status_filter)

    applications = query.order_by(Application.applied_at.desc()).all()
    return [_build_application_response(app_rec) for app_rec in applications]


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: int,
    current_user: User = Depends(all_roles),
    db: Session = Depends(get_db)
):
    """[ALL ROLES] Fetches single application details with permission checks."""
    app_rec = db.query(Application).filter(Application.id == application_id).first()
    if not app_rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {application_id} not found."
        )

    # Permission Scoping
    if current_user.role == UserRole.STUDENT:
        if app_rec.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. You can only view your own applications."
            )
    elif current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == current_user.id).first()
        if not recruiter or recruiter.company_id != app_rec.drive.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. You can only view applications for your company."
            )

    return _build_application_response(app_rec)


@router.put("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_in: ApplicationStatusUpdate,
    current_user: User = Depends(admin_or_recruiter),
    db: Session = Depends(get_db)
):
    """[ADMIN, RECRUITER] Transitions application status enforcing Process State Machine and Recruiter Scoping."""
    updated_app = transition_application_status(
        application_id=application_id,
        target_status=status_in.target_status,
        current_user=current_user,
        db=db
    )
    return _build_application_response(updated_app)
