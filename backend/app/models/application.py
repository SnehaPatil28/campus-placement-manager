import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Enum as SQLEnum, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ApplicationStatus(str, enum.Enum):
    APPLIED = "APPLIED"
    SHORTLISTED = "SHORTLISTED"
    INTERVIEW = "INTERVIEW"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    drive_id = Column(Integer, ForeignKey("placement_drives.id", ondelete="CASCADE"), nullable=False)
    status = Column(SQLEnum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED)
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    student = relationship("Student", backref="applications")
    drive = relationship("PlacementDrive", backref="applications")

    __table_args__ = (
        UniqueConstraint('student_id', 'drive_id', name='uq_student_drive_application'),
    )
