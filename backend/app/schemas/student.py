from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = Field(default=None, ge=0.0, le=10.0)
    backlogs: Optional[int] = Field(default=None, ge=0)
    resume_url: Optional[str] = None
    skills: Optional[List[str]] = None


class StudentProfileResponse(BaseModel):
    id: int
    student_code: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    branch: Optional[str] = None
    graduation_year: Optional[int] = None
    cgpa: Optional[float] = None
    backlogs: int = 0
    resume_url: Optional[str] = None
    skills: List[str] = []
    completeness_percentage: int
    is_profile_complete: bool
    missing_fields: List[str] = []

    model_config = ConfigDict(from_attributes=True)
