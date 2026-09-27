from app.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse, TokenData
from app.schemas.student import StudentProfileUpdate, StudentProfileResponse
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse

__all__ = [
    "UserRegisterRequest", "UserLoginRequest", "TokenResponse", "UserResponse", "TokenData",
    "StudentProfileUpdate", "StudentProfileResponse",
    "CompanyCreate", "CompanyUpdate", "CompanyResponse"
]
