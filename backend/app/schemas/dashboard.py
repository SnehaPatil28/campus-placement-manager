from datetime import datetime
from typing import List, Dict
from pydantic import BaseModel, ConfigDict
from app.schemas.notification import NotificationResponse


class RecentApplicationCard(BaseModel):
    id: int
    drive_id: int
    job_title: str
    company_name: str
    status: str
    applied_at: datetime


class StudentDashboardResponse(BaseModel):
    profile_completion_percentage: float
    is_profile_complete: bool
    eligible_drives_count: int
    active_applications_count: int
    upcoming_interviews_count: int
    offers_received_count: int
    recent_notifications: List[NotificationResponse]
    recent_applications: List[RecentApplicationCard]

    model_config = ConfigDict(from_attributes=True)


class PipelineBreakdown(BaseModel):
    APPLIED: int = 0
    SHORTLISTED: int = 0
    INTERVIEW: int = 0
    SELECTED: int = 0
    REJECTED: int = 0


class RecruiterDashboardResponse(BaseModel):
    company_name: str
    active_drives_count: int
    total_applicants: int
    pipeline_breakdown: Dict[str, int]
    pending_interviews_count: int
    selected_candidates_count: int

    model_config = ConfigDict(from_attributes=True)


class BranchAnalytics(BaseModel):
    branch: str
    total_students: int
    placed_students: int
    placement_percentage: float


class AdminDashboardResponse(BaseModel):
    total_registered_students: int
    total_partner_companies: int
    active_drives_count: int
    total_applications_submitted: int
    placed_students_count: int
    placement_percentage: float
    department_breakdown: List[BranchAnalytics]

    model_config = ConfigDict(from_attributes=True)
