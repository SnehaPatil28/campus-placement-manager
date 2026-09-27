from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import func, distinct
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.student import Student
from app.models.company import Company, Recruiter
from app.models.drive import PlacementDrive, DriveStatus
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview, InterviewResult
from app.models.offer import Offer, OfferStatus
from app.models.notification import Notification

from app.services.drive_service import get_evaluated_drive_status
from app.services.profile_service import calculate_profile_completeness
from app.services.eligibility_service import evaluate_student_eligibility


def get_student_dashboard_metrics(db: Session, student_user_id: int) -> Dict[str, Any]:
    """Calculate aggregate dashboard metrics and activity feed for a student user."""
    student = db.query(Student).filter(Student.id == student_user_id).first()

    if student:
        completeness_pct, is_complete, _ = calculate_profile_completeness(student)
    else:
        completeness_pct, is_complete = 0.0, False

    # 1. Eligible Drives Count
    all_drives = db.query(PlacementDrive).all()
    eligible_drives_count = 0
    if student and is_complete:
        for drive in all_drives:
            if get_evaluated_drive_status(drive) == DriveStatus.OPEN:
                is_elig, _ = evaluate_student_eligibility(student, drive)
                if is_elig:
                    eligible_drives_count += 1
    elif student:
        # Check eligibility even if incomplete if eligible_service supports it, or count 0
        for drive in all_drives:
            if get_evaluated_drive_status(drive) == DriveStatus.OPEN:
                is_elig, _ = evaluate_student_eligibility(student, drive)
                if is_elig:
                    eligible_drives_count += 1

    # 2. Active Applications Count (APPLIED, SHORTLISTED, INTERVIEW)
    active_statuses = [
        ApplicationStatus.APPLIED,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.INTERVIEW,
    ]
    active_apps_count = (
        db.query(func.count(Application.id))
        .filter(
            Application.student_id == student_user_id,
            Application.status.in_(active_statuses),
        )
        .scalar()
        or 0
    )

    # 3. Upcoming Interviews Count
    now_utc = datetime.now(timezone.utc)
    upcoming_interviews_count = (
        db.query(func.count(Interview.id))
        .join(Application, Interview.application_id == Application.id)
        .filter(
            Application.student_id == student_user_id,
            Interview.result == InterviewResult.PENDING,
            Interview.scheduled_time >= now_utc,
        )
        .scalar()
        or 0
    )

    # 4. Offers Received Count
    offers_received_count = (
        db.query(func.count(Offer.id))
        .filter(Offer.student_id == student_user_id)
        .scalar()
        or 0
    )

    # 5. Recent Notifications (top 5)
    recent_notifications = (
        db.query(Notification)
        .filter(Notification.user_id == student_user_id)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )

    # 6. Recent Applications (top 5)
    recent_apps = (
        db.query(Application)
        .filter(Application.student_id == student_user_id)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    recent_app_cards = []
    for app in recent_apps:
        recent_app_cards.append({
            "id": app.id,
            "drive_id": app.drive_id,
            "job_title": app.drive.job_title if app.drive else "N/A",
            "company_name": app.drive.company.name if (app.drive and app.drive.company) else "N/A",
            "status": app.status.value,
            "applied_at": app.applied_at,
        })

    return {
        "profile_completion_percentage": completeness_pct,
        "is_profile_complete": is_complete,
        "eligible_drives_count": eligible_drives_count,
        "active_applications_count": active_apps_count,
        "upcoming_interviews_count": upcoming_interviews_count,
        "offers_received_count": offers_received_count,
        "recent_notifications": recent_notifications,
        "recent_applications": recent_app_cards,
    }


def get_recruiter_dashboard_metrics(db: Session, recruiter_user_id: int) -> Dict[str, Any]:
    """Calculate aggregate metrics for a recruiter based on their associated company."""
    recruiter = db.query(Recruiter).filter(Recruiter.id == recruiter_user_id).first()
    if not recruiter or not recruiter.company_id:
        return {
            "company_name": "Unassigned",
            "active_drives_count": 0,
            "total_applicants": 0,
            "pipeline_breakdown": {
                "APPLIED": 0,
                "SHORTLISTED": 0,
                "INTERVIEW": 0,
                "SELECTED": 0,
                "REJECTED": 0,
            },
            "pending_interviews_count": 0,
            "selected_candidates_count": 0,
        }

    company_id = recruiter.company_id
    company = db.query(Company).filter(Company.id == company_id).first()
    company_name = company.name if company else "Company"

    company_drives = db.query(PlacementDrive).filter(PlacementDrive.company_id == company_id).all()
    company_drive_ids = [d.id for d in company_drives]

    # Active drives count (OPEN or UPCOMING evaluated status)
    active_drives_count = 0
    for drive in company_drives:
        eval_st = get_evaluated_drive_status(drive)
        if eval_st in (DriveStatus.OPEN, DriveStatus.UPCOMING):
            active_drives_count += 1

    if not company_drive_ids:
        return {
            "company_name": company_name,
            "active_drives_count": active_drives_count,
            "total_applicants": 0,
            "pipeline_breakdown": {
                "APPLIED": 0,
                "SHORTLISTED": 0,
                "INTERVIEW": 0,
                "SELECTED": 0,
                "REJECTED": 0,
            },
            "pending_interviews_count": 0,
            "selected_candidates_count": 0,
        }

    # Total applicants across company drives
    total_applicants = (
        db.query(func.count(Application.id))
        .filter(Application.drive_id.in_(company_drive_ids))
        .scalar()
        or 0
    )

    # Pipeline breakdown by status
    pipeline_rows = (
        db.query(Application.status, func.count(Application.id))
        .filter(Application.drive_id.in_(company_drive_ids))
        .group_by(Application.status)
        .all()
    )
    pipeline_breakdown = {
        "APPLIED": 0,
        "SHORTLISTED": 0,
        "INTERVIEW": 0,
        "SELECTED": 0,
        "REJECTED": 0,
    }
    for st, count in pipeline_rows:
        st_key = st.value if hasattr(st, "value") else str(st)
        pipeline_breakdown[st_key] = count

    # Pending interviews count
    pending_interviews_count = (
        db.query(func.count(Interview.id))
        .join(Application, Interview.application_id == Application.id)
        .filter(
            Application.drive_id.in_(company_drive_ids),
            Interview.result == InterviewResult.PENDING,
        )
        .scalar()
        or 0
    )

    # Selected candidates count (status == SELECTED or Offer exists)
    selected_candidates_count = (
        db.query(func.count(distinct(Application.student_id)))
        .filter(
            Application.drive_id.in_(company_drive_ids),
            Application.status == ApplicationStatus.SELECTED,
        )
        .scalar()
        or 0
    )

    return {
        "company_name": company_name,
        "active_drives_count": active_drives_count,
        "total_applicants": total_applicants,
        "pipeline_breakdown": pipeline_breakdown,
        "pending_interviews_count": pending_interviews_count,
        "selected_candidates_count": selected_candidates_count,
    }


def get_admin_dashboard_metrics(db: Session) -> Dict[str, Any]:
    """Calculate system-wide placement drive and recruitment metrics for Admin."""
    total_registered_students = (
        db.query(func.count(User.id))
        .filter(User.role == UserRole.STUDENT)
        .scalar()
        or 0
    )

    total_partner_companies = db.query(func.count(Company.id)).scalar() or 0

    all_drives = db.query(PlacementDrive).all()
    active_drives_count = sum(
        1 for d in all_drives if get_evaluated_drive_status(d) == DriveStatus.OPEN
    )

    total_applications_submitted = db.query(func.count(Application.id)).scalar() or 0

    # Unique students with application status SELECTED or offer status ACCEPTED/OFFERED
    selected_app_student_ids = db.query(Application.student_id).filter(
        Application.status == ApplicationStatus.SELECTED
    )
    offered_student_ids = db.query(Offer.student_id).filter(
        Offer.status.in_([OfferStatus.ACCEPTED, OfferStatus.OFFERED])
    )

    placed_student_ids_set = set(
        s_id for (s_id,) in selected_app_student_ids.all()
    ).union(set(s_id for (s_id,) in offered_student_ids.all()))

    placed_students_count = len(placed_student_ids_set)

    if total_registered_students > 0:
        placement_percentage = round((placed_students_count / total_registered_students) * 100, 2)
    else:
        placement_percentage = 0.0

    # Department breakdown (grouped by branch)
    all_students = db.query(Student).all()
    branch_map: Dict[str, Dict[str, int]] = {}

    for st in all_students:
        branch = st.branch if st.branch else "Unassigned"
        if branch not in branch_map:
            branch_map[branch] = {"total_students": 0, "placed_students": 0}
        branch_map[branch]["total_students"] += 1
        if st.id in placed_student_ids_set:
            branch_map[branch]["placed_students"] += 1

    department_breakdown = []
    for branch_name, counts in branch_map.items():
        tot = counts["total_students"]
        plc = counts["placed_students"]
        pct = round((plc / tot) * 100, 2) if tot > 0 else 0.0
        department_breakdown.append({
            "branch": branch_name,
            "total_students": tot,
            "placed_students": plc,
            "placement_percentage": pct,
        })

    return {
        "total_registered_students": total_registered_students,
        "total_partner_companies": total_partner_companies,
        "active_drives_count": active_drives_count,
        "total_applications_submitted": total_applications_submitted,
        "placed_students_count": placed_students_count,
        "placement_percentage": placement_percentage,
        "department_breakdown": department_breakdown,
    }
