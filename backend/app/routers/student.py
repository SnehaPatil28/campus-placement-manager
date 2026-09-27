from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.student import Student, Skill
from app.schemas.student import StudentProfileUpdate, StudentProfileResponse
from app.auth.dependencies import get_current_user, RoleChecker
from app.services.profile_service import calculate_profile_completeness

router = APIRouter(prefix="/api/v1/students", tags=["Student Management"])

student_only = RoleChecker([UserRole.STUDENT])


def _build_student_response(student: Student) -> StudentProfileResponse:
    pct, is_complete, missing = calculate_profile_completeness(student)
    skill_list = [s.skill_name for s in student.skills] if student.skills else []
    return StudentProfileResponse(
        id=student.id,
        student_code=student.student_code,
        full_name=student.full_name,
        phone=student.phone,
        branch=student.branch,
        graduation_year=student.graduation_year,
        cgpa=student.cgpa,
        backlogs=student.backlogs,
        resume_url=student.resume_url,
        skills=skill_list,
        completeness_percentage=pct,
        is_profile_complete=is_complete,
        missing_fields=missing
    )


@router.get("/me", response_model=StudentProfileResponse)
def get_my_profile(
    current_user: User = Depends(student_only),
    db: Session = Depends(get_db)
):
    """Retrieves current student profile.

    Auto-creates a blank student profile if it does not yet exist.
    """
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        student_code = f"STU{current_user.id:06d}"
        student = Student(
            id=current_user.id,
            student_code=student_code,
            full_name=None,
            phone=None,
            branch=None,
            graduation_year=None,
            cgpa=None,
            backlogs=0,
            resume_url=None
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    return _build_student_response(student)


@router.put("/me", response_model=StudentProfileResponse)
def update_my_profile(
    profile_data: StudentProfileUpdate,
    current_user: User = Depends(student_only),
    db: Session = Depends(get_db)
):
    """Updates current student profile fields and syncs skill tags."""
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        student_code = f"STU{current_user.id:06d}"
        student = Student(
            id=current_user.id,
            student_code=student_code
        )
        db.add(student)
        db.commit()
        db.refresh(student)

    # Update scalar fields if provided
    update_data = profile_data.model_dump(exclude_unset=True)
    skills_input = update_data.pop("skills", None)

    for key, value in update_data.items():
        setattr(student, key, value)

    # Replace/sync skills if skills list provided
    if skills_input is not None:
        db.query(Skill).filter(Skill.student_id == student.id).delete()
        # Deduplicate skill names case-insensitively while preserving original casing
        seen = set()
        for skill_str in skills_input:
            clean_skill = skill_str.strip()
            if clean_skill and clean_skill.lower() not in seen:
                seen.add(clean_skill.lower())
                new_skill = Skill(student_id=student.id, skill_name=clean_skill)
                db.add(new_skill)

    db.commit()
    db.refresh(student)
    return _build_student_response(student)
