import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class DriveStatus(str, enum.Enum):
    UPCOMING = "UPCOMING"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class PlacementDrive(Base):
    __tablename__ = "placement_drives"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    job_title = Column(String, index=True, nullable=False)
    job_description = Column(Text, nullable=False)
    package_lpa = Column(Float, nullable=False)
    location = Column(String, nullable=False)
    min_cgpa = Column(Float, nullable=False)
    max_backlogs = Column(Integer, nullable=False, default=0)
    graduation_year = Column(Integer, nullable=False)
    allowed_branches = Column(String, nullable=False)  # Comma-separated: "CSE,IT,AIML"
    required_skills = Column(String, nullable=False)   # Comma-separated: "Python,SQL"
    application_deadline = Column(DateTime, nullable=False)
    status = Column(SQLEnum(DriveStatus), nullable=False, default=DriveStatus.OPEN)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    company = relationship("Company", backref="placement_drives")
