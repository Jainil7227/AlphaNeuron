from sqlalchemy import Column, String, Float, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class UserType(str, enum.Enum):
    """User type enumeration."""
    DRIVER = "driver"
    FLEET_OPERATOR = "fleet_operator"
    ADMIN = "admin"


class User(Base):
    """
    User model for drivers, fleet operators, and admins.
    
    Supports multi-stakeholder system:
    - Drivers: Individual truck drivers
    - Fleet Operators: Manage multiple vehicles and drivers
    - Admin: System administrators
    """
    
    # Authentication
    type = Column(Enum(UserType), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    
    # Status
    rating = Column(Float, default=5.0)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Profile
    avatar_url = Column(Text, nullable=True)
    
    # Preferences (JSON)
    preferences = Column(
        JSONB,
        default=lambda: {
            "language": "en",
            "notifications": {"push": True, "sms": True, "email": False},
        },
    )
    
    # Driver-specific fields
    license_number = Column(String(50), nullable=True)
    license_expiry = Column(String(10), nullable=True)
    experience_years = Column(Float, nullable=True)
    total_trips = Column(Float, default=0)
    total_earnings = Column(Float, default=0.0)
    
    # Fleet operator fields
    company_name = Column(String(200), nullable=True)
    gst_number = Column(String(20), nullable=True)
    
    # Relationships
    owned_vehicles = relationship(
        "Vehicle",
        back_populates="owner",
        foreign_keys="Vehicle.owner_id",
    )
    
    operated_missions = relationship(
        "Mission",
        back_populates="operator",
        foreign_keys="Mission.operator_id",
    )
    
    driven_missions = relationship(
        "Mission",
        back_populates="driver",
        foreign_keys="Mission.driver_id",
    )
    
    # Helper properties
    @property
    def is_driver(self) -> bool:
        return self.type == UserType.DRIVER
    
    @property
    def is_fleet_operator(self) -> bool:
        return self.type == UserType.FLEET_OPERATOR
    
    @property
    def is_admin(self) -> bool:
        return self.type == UserType.ADMIN
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name}, type={self.type})>"
