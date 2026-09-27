from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.company import Recruiter
from app.models.application import Application, ApplicationStatus
from app.models.interview import Interview, InterviewResult
from app.models.offer import Offer, OfferStatus
from app.schemas.offer import OfferCreate, OfferStatusUpdate


from app.services.notification_service import create_notification


def create_offer(db: Session, recruiter_user: User, offer_in: OfferCreate) -> Offer:
    app_record = db.query(Application).filter(Application.id == offer_in.application_id).first()
    if not app_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Application with ID {offer_in.application_id} not found."
        )

    # 1. Recruiter Company Boundary Guard
    if recruiter_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.id == recruiter_user.id).first()
        if not recruiter or recruiter.company_id != app_record.drive.company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted. You can only generate offers for your company's drives."
            )

    # 2. Selection Eligibility Guard: Candidate MUST have completed & PASSED an interview
    passed_interview = db.query(Interview).filter(
        Interview.application_id == app_record.id,
        Interview.result == InterviewResult.PASSED
    ).first()

    if not passed_interview:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only candidates who have completed and PASSED an interview can be selected and offered."
        )

    # 3. Duplicate Offer Guard
    existing_offer = db.query(Offer).filter(Offer.application_id == app_record.id).first()
    if existing_offer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An offer has already been generated for this candidate's application."
        )

    # 4. State Transition & Offer Generation
    app_record.status = ApplicationStatus.SELECTED

    new_offer = Offer(
        application_id=app_record.id,
        student_id=app_record.student_id,
        drive_id=app_record.drive_id,
        package_offered=offer_in.package_offered,
        joining_date=offer_in.joining_date,
        status=OfferStatus.OFFERED
    )

    db.add(new_offer)

    # Trigger In-App Notification Event for Offer Received
    company_name = app_record.drive.company.name if (app_record.drive and app_record.drive.company) else "Company"
    job_title = app_record.drive.job_title if app_record.drive else "Job Position"
    create_notification(
        db=db,
        user_id=app_record.student_id,
        title="Congratulations! Offer Received",
        message=f"You have been selected for {job_title} at {company_name} with a package of ₹{new_offer.package_offered} LPA!"
    )

    db.commit()
    db.refresh(new_offer)
    return new_offer


def respond_to_offer(db: Session, student_user: User, offer_id: int, status_update: OfferStatusUpdate) -> Offer:
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Offer with ID {offer_id} not found."
        )

    # Student Ownership Guard
    if offer.student_id != student_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. You can only respond to your own offers."
        )

    offer.status = status_update.status
    db.commit()
    db.refresh(offer)
    return offer
