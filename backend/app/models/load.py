from sqlalchemy import Column, String, Float, Integer, Enum, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.db.base import Base


class LoadStatus(str, enum.Enum):
    """Load lifecycle status."""
    POSTED = "posted"
    MATCHED = "matched"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class CargoType(str, enum.Enum):
    """Type of cargo."""
    GENERAL = "general"
    FRAGILE = "fragile"
    PERISHABLE = "perishable"
    HAZARDOUS = "hazardous"
    ELECTRONICS = "electronics"
    MACHINERY = "machinery"
    TEXTILES = "textiles"
    FMCG = "fmcg"
    AGRICULTURAL = "agricultural"
    CONSTRUCTION = "construction"


class RateType(str, enum.Enum):
    """Pricing rate type."""
    PER_KM = "per_km"
    PER_TON = "per_ton"
    FIXED = "fixed"


class Load(Base):
    """
    Load model for freight/cargo.
    
    Supports:
    - LTL (Less Than Truckload) pooling
    - Backhaul matching
    - Time window constraints
    - Shipper ratings
    """
    
    # Shipper Info
    shipper_id = Column(String(50), nullable=True)
    shipper_name = Column(String(100), nullable=False)
    shipper_phone = Column(String(15), nullable=False)
    shipper_rating = Column(Float, default=5.0)
    
    # Cargo Details
    cargo_type = Column(Enum(CargoType), default=CargoType.GENERAL, nullable=False)
    description = Column(Text, nullable=True)
    weight_tons = Column(Float, nullable=False)
    volume_cbm = Column(Float, nullable=True)
    
    # Pickup - PostGIS
    pickup_location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    pickup_address = Column(String(500), nullable=False)
    pickup_city = Column(String(100), nullable=False)
    pickup_window_start = Column(String(30), nullable=False)
    pickup_window_end = Column(String(30), nullable=False)
    
    # Delivery - PostGIS
    delivery_location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    delivery_address = Column(String(500), nullable=False)
    delivery_city = Column(String(100), nullable=False)
    delivery_window_start = Column(String(30), nullable=True)
    delivery_window_end = Column(String(30), nullable=True)
    
    # Pricing
    offered_rate = Column(Float, nullable=False)
    rate_type = Column(Enum(RateType), default=RateType.FIXED, nullable=False)
    negotiable = Column(Boolean, default=True)
    
    # Status
    status = Column(Enum(LoadStatus), default=LoadStatus.POSTED, nullable=False, index=True)
    
    # Matching
    matched_mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=True)
    
    # Posting
    posted_at = Column(String(30), nullable=False)
    expires_at = Column(String(30), nullable=True)
    
    # Special requirements
    requires_cover = Column(Boolean, default=False)
    requires_crane = Column(Boolean, default=False)
    special_instructions = Column(Text, nullable=True)
    
    # Relationships
    mission_loads = relationship("MissionLoad", back_populates="load")
    
    # Properties
    @property
    def is_available(self) -> bool:
        return self.status == LoadStatus.POSTED
    
    @property
    def is_ltl(self) -> bool:
        """Check if this is a partial load (LTL)."""
        return self.weight_tons < 5  # Less than 5 tons = LTL
    
    @property
    def display_rate(self) -> str:
        if self.rate_type == RateType.PER_KM:
            return f"₹{self.offered_rate}/km"
        elif self.rate_type == RateType.PER_TON:
            return f"₹{self.offered_rate}/ton"
        return f"₹{self.offered_rate}"


class MissionLoad(Base):
    """
    Junction table linking missions to loads.
    Supports multiple loads per mission (LTL pooling).
    """
    
    __tablename__ = "mission_loads"
    
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False, index=True)
    load_id = Column(UUID(as_uuid=True), ForeignKey("loads.id"), nullable=False, index=True)
    
    sequence = Column(Integer, nullable=False)
    
    # Status tracking
    status = Column(String(20), default="assigned")
    picked_at = Column(String(30), nullable=True)
    delivered_at = Column(String(30), nullable=True)
    
    # Fare for this specific load
    fare_amount = Column(Float, nullable=True)
    
    # Relationships
    mission = relationship("Mission", back_populates="loads")
    load = relationship("Load", back_populates="mission_loads")
