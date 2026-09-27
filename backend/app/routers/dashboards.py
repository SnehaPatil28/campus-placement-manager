from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.dependencies import RoleChecker
from app.schemas.dashboard import (
    StudentDashboardResponse,
    RecruiterDashboardResponse,
    AdminDashboardResponse,
)
from app.services import dashboard_service

router = APIRouter(prefix="/api/v1/dashboards", tags=["Dashboards"])


@router.get("/student", response_model=StudentDashboardResponse, status_code=status.HTTP_200_OK)
def get_student_dashboard(
    current_user: User = Depends(RoleChecker([UserRole.STUDENT])),
    db: Session = Depends(get_db),
):
    """Protected STUDENT endpoint. Returns personalized student metrics and recent feed."""
    return dashboard_service.get_student_dashboard_metrics(
        db=db, student_user_id=current_user.id
    )


@router.get("/recruiter", response_model=RecruiterDashboardResponse, status_code=status.HTTP_200_OK)
def get_recruiter_dashboard(
    current_user: User = Depends(RoleChecker([UserRole.RECRUITER])),
    db: Session = Depends(get_db),
):
    """Protected RECRUITER endpoint. Returns company drive pipeline metrics."""
    return dashboard_service.get_recruiter_dashboard_metrics(
        db=db, recruiter_user_id=current_user.id
    )


@router.get("/admin", response_model=AdminDashboardResponse, status_code=status.HTTP_200_OK)
def get_admin_dashboard(
    current_user: User = Depends(RoleChecker([UserRole.ADMIN])),
    db: Session = Depends(get_db),
):
    """Protected ADMIN endpoint. Returns system-wide placement analytics and branch breakdown."""
    return dashboard_service.get_admin_dashboard_metrics(db=db)
