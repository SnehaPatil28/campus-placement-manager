from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.offer import OfferStatus


class OfferCreate(BaseModel):
    application_id: int
    package_offered: float
    joining_date: date


class OfferStatusUpdate(BaseModel):
    status: OfferStatus


class OfferResponse(BaseModel):
    id: int
    application_id: int
    student_id: int
    student_name: Optional[str] = None
    student_code: str
    drive_id: int
    job_title: str
    company_name: str
    package_offered: float
    joining_date: date
    status: OfferStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
