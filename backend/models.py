from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime

class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.strip()

class UserSignup(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        return v.strip()

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[str] = None # Keeping as str for simplicity in JSON
    avatar_url: Optional[str] = None

class InsuranceCreate(BaseModel):
    provider_name: str
    policy_number: str
    policy_type: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    premium_amount: float
    coverage_amount: float
    status: str = "Active"

class SettingsUpdate(BaseModel):
    theme_mode: Optional[str] = None
    notifications_enabled: Optional[bool] = None
    biometric_login: Optional[bool] = None
    language: Optional[str] = None
