import uuid
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
from app.models.profile import GenderEnum, BloodGroupEnum

class ProfileCreateUpdateRequest(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: GenderEnum = Field(default=GenderEnum.PREFER_NOT_TO_SAY)
    blood_group: BloodGroupEnum = Field(default=BloodGroupEnum.UNKNOWN)
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)

class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: str
    blood_group: str
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    class Config:
        from_attributes = True
