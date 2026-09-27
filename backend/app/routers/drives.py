from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.models.student import Student
from app.models.drive import PlacementDrive, DriveStatus
from app.schemas.drive import (
    PlacementDriveCreate, PlacementDriveUpdate, PlacementDriveResponse, EligibilityCheckResponse
)
from app.auth.dependencies import get_current_user, RoleChecker
from app.services.drive_service import get_evaluated_drive_status, parse_csv_list, format_list_to_csv
from app.services.eligibility_service import evaluate_student_eligibility
from app.services.profile_service import calculate_profile_completeness

router = APIRouter(prefix="/api/v1/drives", tags=["Placement Drive Management"])

admin_only = RoleChecker([UserRole.ADMIN])
student_only = RoleChecker([UserRole.STUDENT])
all_roles = RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.STUDENT])


def _build_drive_response(drive: PlacementDrive) -> PlacementDriveResponse:
    eval_status = get_evaluated_drive_status(drive)
    company_name = drive.company.name if drive.company else "Unknown"
    return PlacementDriveResponse(
        id=drive.id,
        company_id=drive.company_id,
        company_name=company_name,
        job_title=drive.job_title,
        job_description=drive.job_description,
        package_lpa=drive.package_lpa,
        location=drive.location,
        min_cgpa=drive.min_cgpa,
        max_backlogs=drive.max_backlogs,
        graduation_year=drive.graduation_year,
        allowed_branches=parse_csv_list(drive.allowed_branches),
        required_skills=parse_csv_list(drive.required_skills),
        application_deadline=drive.application_deadline,
        status=eval_status,
        created_at=drive.created_at
    )


@router.post("", response_model=PlacementDriveResponse, status_code=status.HTTP_201_CREATED)
def create_placement_drive(
    drive_in: PlacementDriveCreate,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """[ADMIN] Creates a placement drive linked to an existing company."""
    company = db.query(Company).filter(Company.id == drive_in.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {drive_in.company_id} does not exist."
        )

    drive = PlacementDrive(
        company_id=drive_in.company_id,
        job_title=drive_in.job_title,
        job_description=drive_in.job_description,
        package_lpa=drive_in.package_lpa,
        location=drive_in.location,
        min_cgpa=drive_in.min_cgpa,
        max_backlogs=drive_in.max_backlogs,
        graduation_year=drive_in.graduation_year,
        allowed_branches=format_list_to_csv(drive_in.allowed_branches),
        required_skills=format_list_to_csv(drive_in.required_skills),
        application_deadline=drive_in.application_deadline,
        status=drive_in.status
    )
    db.add(drive)
    db.commit()
    db.refresh(drive)
    return _build_drive_response(drive)


@router.get("", response_model=List[PlacementDriveResponse])
def list_placement_drives(
    status_filter: Optional[DriveStatus] = None,
    company_id: Optional[int] = None,
    current_user: User = Depends(all_roles),
    db: Session = Depends(get_db)
):
    """[ALL ROLES] Lists all placement drives with dynamic status evaluations."""
    query = db.query(PlacementDrive)
    if company_id is not None:
        query = query.filter(PlacementDrive.company_id == company_id)

    drives = query.order_by(PlacementDrive.created_at.desc()).all()

    # Build responses with computed status and filter if status_filter supplied
    responses = []
    for d in drives:
        res = _build_drive_response(d)
        if status_filter is None or res.status == status_filter:
            responses.append(res)

    return responses


@router.get("/{drive_id}", response_model=PlacementDriveResponse)
def get_placement_drive(
    drive_id: int,
    current_user: User = Depends(all_roles),
    db: Session = Depends(get_db)
):
    """[ALL ROLES] Fetches single placement drive details."""
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Placement Drive with ID {drive_id} not found."
        )
    return _build_drive_response(drive)


@router.put("/{drive_id}", response_model=PlacementDriveResponse)
def update_placement_drive(
    drive_id: int,
    drive_in: PlacementDriveUpdate,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """[ADMIN] Updates placement drive details and criteria."""
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Placement Drive with ID {drive_id} not found."
        )

    update_data = drive_in.model_dump(exclude_unset=True)

    if "allowed_branches" in update_data and update_data["allowed_branches"] is not None:
        update_data["allowed_branches"] = format_list_to_csv(update_data["allowed_branches"])

    if "required_skills" in update_data and update_data["required_skills"] is not None:
        update_data["required_skills"] = format_list_to_csv(update_data["required_skills"])

    for field, value in update_data.items():
        setattr(drive, field, value)

    db.commit()
    db.refresh(drive)
    return _build_drive_response(drive)


@router.get("/{drive_id}/eligibility", response_model=EligibilityCheckResponse)
def check_drive_eligibility(
    drive_id: int,
    current_user: User = Depends(student_only),
    db: Session = Depends(get_db)
):
    """[STUDENT] Runs the backend eligibility engine for the logged-in student against the target drive."""
    drive = db.query(PlacementDrive).filter(PlacementDrive.id == drive_id).first()
    if not drive:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Placement Drive with ID {drive_id} not found."
        )

    # Get student profile (auto-create blank profile if missing)
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        student = Student(id=current_user.id, student_code=f"STU{current_user.id:06d}")
        db.add(student)
        db.commit()
        db.refresh(student)

    _, is_profile_complete, _ = calculate_profile_completeness(student)
    is_eligible, reasons = evaluate_student_eligibility(student, drive)

    student_skills_list = [s.skill_name for s in student.skills] if student.skills else []

    return EligibilityCheckResponse(
        drive_id=drive.id,
        drive_title=drive.job_title,
        is_eligible=is_eligible,
        is_profile_complete=is_profile_complete,
        reasons=reasons,
        student_metrics={
            "cgpa": student.cgpa,
            "branch": student.branch,
            "graduation_year": student.graduation_year,
            "backlogs": student.backlogs,
            "skills": student_skills_list
        },
        drive_criteria={
            "min_cgpa": drive.min_cgpa,
            "allowed_branches": parse_csv_list(drive.allowed_branches),
            "graduation_year": drive.graduation_year,
            "max_backlogs": drive.max_backlogs,
            "required_skills": parse_csv_list(drive.required_skills)
        }
    )
