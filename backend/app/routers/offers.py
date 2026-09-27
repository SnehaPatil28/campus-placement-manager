from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Recruiter
from app.models.drive import PlacementDrive
from app.models.offer import Offer
from app.schemas.offer import OfferCreate, OfferStatusUpdate, OfferResponse
from app.auth.dependencies import RoleChecker
from app.services.offer_service import create_offer, respond_to_offer

router = APIRouter(prefix="/api/v1/offers", tags=["Offer Management"])

recruiter_only = RoleChecker([UserRole.RECRUITER])
student_only = RoleChecker([UserRole.STUDENT])
all_roles = RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.STUDENT])


def _build_offer_response(offer: Offer) -> OfferResponse:
    student = offer.student
    drive = offer.drive
    company_name = drive.company.name if (drive and drive.company) else "Unknown"

    return OfferResponse(
        id=offer.id,
        application_id=offer.application_id,
        student_id=offer.student_id,
        student_name=student.full_name if student else None,
        student_code=student.student_code if student else f"STU{offer.student_id:06d}",
        drive_id=offer.drive_id,
        job_title=drive.job_title if drive else "",
        company_name=company_name,
        package_offered=offer.package_offered,
        joining_date=offer.joining_date,
        status=offer.status,
        created_at=offer.created_at
    )


@router.post("", response_model=OfferResponse, status_code=status.HTTP_201_CREATED)
def issue_job_offer(
    offer_in: OfferCreate,
    current_user: User = Depends(recruiter_only),
    db: Session = Depends(get_db)
):
    """[RECRUITER] Generates an employment offer for a candidate who passed an interview round and transitions application to SELECTED status."""
    new_offer = create_offer(db=db, recruiter_user=current_user, offer_in=offer_in)
    return _build_offer_response(new_offer)


@router.get("", response_model=List[OfferResponse])
def list_offers(
    current_user: User = Depends(all_roles),
    db: Session = Depends(get_db)
):
    """[ALL ROLES] Lists extended job offers scoped by user role and company boundaries."""
    query = db.query(Offer).join(PlacementDrive)

    if current_user.role == UserRole.STUDENT:
        query = query.filter(Offer.student_id == current_user.id)
    elif current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == current_user.id).first()
        if not recruiter:
            return []
        query = query.filter(PlacementDrive.company_id == recruiter.company_id)

    offers = query.order_by(Offer.created_at.desc()).all()
    return [_build_offer_response(off) for off in offers]


@router.put("/{offer_id}/status", response_model=OfferResponse)
def respond_to_job_offer(
    offer_id: int,
    status_in: OfferStatusUpdate,
    current_user: User = Depends(student_only),
    db: Session = Depends(get_db)
):
    """[STUDENT] Accepts or declines an extended employment offer."""
    updated_offer = respond_to_offer(
        db=db,
        student_user=current_user,
        offer_id=offer_id,
        status_update=status_in
    )
    return _build_offer_response(updated_offer)
