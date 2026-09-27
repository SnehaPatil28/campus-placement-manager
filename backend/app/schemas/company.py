from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CompanyCreate(BaseModel):
    name: str
    industry: str
    location: str
    is_active: bool = True


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    industry: str
    location: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
