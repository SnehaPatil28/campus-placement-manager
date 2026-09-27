from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.interview import InterviewMode, InterviewResult


class InterviewCreate(BaseModel):
    application_id: int
    scheduled_time: datetime
    mode: InterviewMode = InterviewMode.ONLINE
    location_or_link: str


class InterviewResultUpdate(BaseModel):
    result: InterviewResult
    feedback: Optional[str] = None


class InterviewResponse(BaseModel):
    id: int
    application_id: int
    student_id: int
    student_name: Optional[str] = None
    student_code: str
    job_title: str
    company_name: str
    scheduled_time: datetime
    mode: InterviewMode
    location_or_link: str
    result: InterviewResult
    feedback: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
