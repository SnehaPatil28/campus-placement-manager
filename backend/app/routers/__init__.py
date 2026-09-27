from app.routers.auth import router as auth_router
from app.routers.student import router as student_router
from app.routers.company import router as company_router

__all__ = ["auth_router", "student_router", "company_router"]
