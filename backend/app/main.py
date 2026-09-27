from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import (
    auth_router, student_router, company_router,
    drives_router, applications_router,
    interviews_router, offers_router,
    notifications_router, dashboards_router
)

# Auto-create SQLite database tables on server initialization
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="College Placement Manager API",
    description="Campus Recruitment & Placement System Backend",
    version="1.0.0"
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(company_router)
app.include_router(drives_router)
app.include_router(applications_router)
app.include_router(interviews_router)
app.include_router(offers_router)
app.include_router(notifications_router)
app.include_router(dashboards_router)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint returning system status."""
    return {
        "status": "healthy",
        "service": "College Placement Manager API",
        "version": "1.0.0"
    }
