import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Enum as SQLEnum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class InterviewMode(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class InterviewResult(str, enum.Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id", ondelete="CASCADE"), nullable=False, index=True)
    scheduled_time = Column(DateTime, nullable=False)
    mode = Column(SQLEnum(InterviewMode), nullable=False, default=InterviewMode.ONLINE)
    location_or_link = Column(String, nullable=False)
    result = Column(SQLEnum(InterviewResult), nullable=False, default=InterviewResult.PENDING)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship
    application = relationship("Application", backref="interviews")
