from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.models.drive import DriveStatus


class PlacementDriveCreate(BaseModel):
    company_id: int
    job_title: str
    job_description: str
    package_lpa: float = Field(gt=0)
    location: str
    min_cgpa: float = Field(ge=0.0, le=10.0)
    max_backlogs: int = Field(ge=0, default=0)
    graduation_year: int
    allowed_branches: List[str]
    required_skills: List[str]
    application_deadline: datetime
    status: DriveStatus = DriveStatus.OPEN


class PlacementDriveUpdate(BaseModel):
    job_title: Optional[str] = None
    job_description: Optional[str] = None
    package_lpa: Optional[float] = Field(default=None, gt=0)
    location: Optional[str] = None
    min_cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    max_backlogs: Optional[int] = Field(default=None, ge=0)
    graduation_year: Optional[int] = None
    allowed_branches: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    application_deadline: Optional[datetime] = None
    status: Optional[DriveStatus] = None


class PlacementDriveResponse(BaseModel):
    id: int
    company_id: int
    company_name: str
    job_title: str
    job_description: str
    package_lpa: float
    location: str
    min_cgpa: float
    max_backlogs: int
    graduation_year: int
    allowed_branches: List[str]
    required_skills: List[str]
    application_deadline: datetime
    status: DriveStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EligibilityCheckResponse(BaseModel):
    drive_id: int
    drive_title: str
    is_eligible: bool
    is_profile_complete: bool
    reasons: List[str]
    student_metrics: Dict[str, Any]
    drive_criteria: Dict[str, Any]
