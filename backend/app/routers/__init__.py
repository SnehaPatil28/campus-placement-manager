from app.routers.auth import router as auth_router
from app.routers.student import router as student_router
from app.routers.company import router as company_router
from app.routers.drives import router as drives_router
from app.routers.applications import router as applications_router
from app.routers.interviews import router as interviews_router
from app.routers.offers import router as offers_router
from app.routers.notifications import router as notifications_router
from app.routers.dashboards import router as dashboards_router

__all__ = [
    "auth_router", "student_router", "company_router",
    "drives_router", "applications_router",
    "interviews_router", "offers_router",
    "notifications_router", "dashboards_router"
]
