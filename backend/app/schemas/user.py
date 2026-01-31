from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.user import UserType


# Base schema with common fields
class UserBase(BaseModel):
    """Base user schema with common fields."""
    name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")  # Indian mobile
    email: Optional[EmailStr] = None
    

# Registration
class UserRegister(UserBase):
    """Schema for user registration."""
    type: UserType
    password: str = Field(..., min_length=6)
    
    # Driver fields
    license_number: Optional[str] = None
    experience_years: Optional[float] = None
    
    # Fleet operator fields
    company_name: Optional[str] = None
    gst_number: Optional[str] = Field(None, pattern=r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")


# Login
class UserLogin(BaseModel):
    """Schema for user login."""
    phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    password: str


# Token response
class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh request."""
    refresh_token: str


# Profile update
class UserUpdate(BaseModel):
    """Schema for profile update."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    
    # Driver fields
    license_number: Optional[str] = None
    license_expiry: Optional[str] = None
    experience_years: Optional[float] = None
    
    # Fleet operator fields
    company_name: Optional[str] = None
    gst_number: Optional[str] = None
    
    # Preferences
    preferences: Optional[dict] = None


# Response schemas
class UserResponse(UserBase):
    """User response schema."""
    id: UUID
    type: UserType
    rating: float
    is_verified: bool
    is_active: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    
    # Driver fields
    license_number: Optional[str] = None
    experience_years: Optional[float] = None
    total_trips: Optional[float] = None
    total_earnings: Optional[float] = None
    
    # Fleet operator fields
    company_name: Optional[str] = None
    gst_number: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserBrief(BaseModel):
    """Brief user info for references."""
    id: UUID
    name: str
    phone: str
    type: UserType
    rating: float
    
    class Config:
        from_attributes = True


# Driver-specific response
class DriverResponse(UserResponse):
    """Extended driver response with stats."""
    license_expiry: Optional[str] = None
    preferences: Optional[dict] = None


# Fleet operator response
class FleetOperatorResponse(UserResponse):
    """Extended fleet operator response."""
    preferences: Optional[dict] = None
    vehicle_count: Optional[int] = None
    active_missions: Optional[int] = None
