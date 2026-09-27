from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, TokenData
from app.schemas.student import StudentProfileUpdate, StudentProfileResponse
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.schemas.drive import PlacementDriveCreate, PlacementDriveUpdate, PlacementDriveResponse, EligibilityCheckResponse
from app.schemas.application import ApplicationCreate, ApplicationStatusUpdate, ApplicationResponse
from app.schemas.interview import InterviewCreate, InterviewResultUpdate, InterviewResponse
from app.schemas.offer import OfferCreate, OfferStatusUpdate, OfferResponse
from app.schemas.notification import NotificationResponse, NotificationUnreadCount
from app.schemas.dashboard import StudentDashboardResponse, RecruiterDashboardResponse, AdminDashboardResponse

__all__ = [
    "UserRegisterRequest", "UserLoginRequest", "TokenResponse", "UserResponse", "TokenData",
    "StudentProfileUpdate", "StudentProfileResponse",
    "CompanyCreate", "CompanyUpdate", "CompanyResponse",
    "PlacementDriveCreate", "PlacementDriveUpdate", "PlacementDriveResponse", "EligibilityCheckResponse",
    "ApplicationCreate", "ApplicationStatusUpdate", "ApplicationResponse",
    "InterviewCreate", "InterviewResultUpdate", "InterviewResponse",
    "OfferCreate", "OfferStatusUpdate", "OfferResponse",
    "NotificationResponse", "NotificationUnreadCount",
    "StudentDashboardResponse", "RecruiterDashboardResponse", "AdminDashboardResponse"
]
