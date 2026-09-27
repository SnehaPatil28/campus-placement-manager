from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    drive_id: int


class ApplicationStatusUpdate(BaseModel):
    target_status: ApplicationStatus


class ApplicationResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    student_code: str
    student_branch: Optional[str] = None
    student_cgpa: Optional[float] = None
    drive_id: int
    job_title: str
    company_name: str
    status: ApplicationStatus
    applied_at: datetime

    model_config = ConfigDict(from_attributes=True)
