from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, UserRole
from app.models.company import Company
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.auth.dependencies import RoleChecker

router = APIRouter(prefix="/api/v1/companies", tags=["Company Management"])

admin_only = RoleChecker([UserRole.ADMIN])
admin_or_recruiter = RoleChecker([UserRole.ADMIN, UserRole.RECRUITER])


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def create_company(
    company_in: CompanyCreate,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """[ADMIN] Registers a new company. Rejects duplicate company names."""
    existing = db.query(Company).filter(Company.name == company_in.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with name '{company_in.name}' already exists."
        )

    company = Company(
        name=company_in.name,
        industry=company_in.industry,
        location=company_in.location,
        is_active=company_in.is_active
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("", response_model=List[CompanyResponse])
def list_companies(
    active_only: bool = False,
    current_user: User = Depends(admin_or_recruiter),
    db: Session = Depends(get_db)
):
    """[ADMIN, RECRUITER] Lists companies. Option to filter active companies only."""
    query = db.query(Company)
    if active_only:
        query = query.filter(Company.is_active.is_(True))
    return query.order_by(Company.name.asc()).all()


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: int,
    current_user: User = Depends(admin_or_recruiter),
    db: Session = Depends(get_db)
):
    """[ADMIN, RECRUITER] Fetches detailed company profile by ID."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: int,
    company_in: CompanyUpdate,
    current_user: User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """[ADMIN] Updates company parameters or toggles active status."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found."
        )

    update_data = company_in.model_dump(exclude_unset=True)
    if "name" in update_data and update_data["name"] != company.name:
        dup = db.query(Company).filter(Company.name == update_data["name"]).first()
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Company name '{update_data['name']}' is already in use."
            )

    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)
    return company
