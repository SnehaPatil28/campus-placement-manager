import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Date, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class OfferStatus(str, enum.Enum):
    OFFERED = "OFFERED"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), unique=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    drive_id = Column(Integer, ForeignKey("placement_drives.id", ondelete="CASCADE"), nullable=False)
    package_offered = Column(Float, nullable=False)
    joining_date = Column(Date, nullable=False)
    status = Column(SQLEnum(OfferStatus), nullable=False, default=OfferStatus.OFFERED)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    application = relationship("Application", backref="offer", uselist=False)
    student = relationship("Student", backref="offers")
    drive = relationship("PlacementDrive", backref="offers")
