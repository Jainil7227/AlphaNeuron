from sqlalchemy import Column, String, Float, Integer, Enum, Date, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.db.base import Base


class VehicleType(str, enum.Enum):
    """Indian logistics vehicle categories."""
    MINI_TRUCK = "mini_truck"      # Tata Ace, Mahindra Bolero
    LCV = "lcv"                     # Light Commercial < 7.5 ton
    ICV = "icv"                     # Intermediate 7.5-12 ton
    MCV = "mcv"                     # Medium 12-16 ton
    HCV = "hcv"                     # Heavy 16-25 ton
    MAV = "mav"                     # Multi-Axle > 25 ton
    TRAILER = "trailer"
    CONTAINER = "container"


class VehicleStatus(str, enum.Enum):
    """Vehicle operational status."""
    AVAILABLE = "available"
    ON_MISSION = "on_mission"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class FuelType(str, enum.Enum):
    """Fuel type enumeration."""
    DIESEL = "diesel"
    PETROL = "petrol"
    CNG = "cng"
    ELECTRIC = "electric"


class Vehicle(Base):
    """
    Vehicle model for trucks in logistics system.
    
    Supports:
    - Indian vehicle categories (LCV, HCV, etc.)
    - Real-time PostGIS location tracking
    - LTL capacity management
    - Indian compliance (insurance, fitness, permits)
    """
    
    # Owner
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Identification
    registration_number = Column(String(20), unique=True, nullable=False, index=True)
    vehicle_type = Column(Enum(VehicleType), nullable=False, index=True)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    
    # Dimensions (JSON)
    dimensions = Column(JSONB, default=lambda: {"length_m": 0, "width_m": 0, "height_m": 0})
    
    # Capacity - Critical for LTL
    max_capacity_tons = Column(Float, nullable=False)
    current_load_tons = Column(Float, default=0.0)
    volume_capacity_cbm = Column(Float, nullable=True)
    current_volume_cbm = Column(Float, default=0.0)
    
    # Status
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False, index=True)
    
    # Location - PostGIS
    current_location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    last_location_update = Column(String(30), nullable=True)
    
    # Fuel
    fuel_type = Column(Enum(FuelType), default=FuelType.DIESEL, nullable=False)
    fuel_level_percent = Column(Float, default=100.0)
    tank_capacity_liters = Column(Float, nullable=True)
    avg_fuel_efficiency = Column(Float, nullable=True)
    
    # Indian Compliance
    insurance_expiry = Column(Date, nullable=True)
    fitness_expiry = Column(Date, nullable=True)
    permit_type = Column(String(50), nullable=True)
    permit_states = Column(JSONB, default=list)
    permit_expiry = Column(Date, nullable=True)
    puc_expiry = Column(Date, nullable=True)
    
    # Assignment
    assigned_driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    current_mission_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Statistics
    total_trips = Column(Integer, default=0)
    total_km = Column(Float, default=0.0)
    
    # Images
    images = Column(JSONB, default=list)
    
    # Relationships
    owner = relationship("User", back_populates="owned_vehicles", foreign_keys=[owner_id])
    missions = relationship("Mission", back_populates="vehicle", foreign_keys="Mission.vehicle_id")
    location_history = relationship("VehicleLocation", back_populates="vehicle", order_by="desc(VehicleLocation.recorded_at)")
    
    # Properties for LTL
    @property
    def available_capacity_tons(self) -> float:
        return max(0, self.max_capacity_tons - self.current_load_tons)
    
    @property
    def capacity_utilization_percent(self) -> float:
        if self.max_capacity_tons == 0:
            return 0
        return (self.current_load_tons / self.max_capacity_tons) * 100
    
    @property
    def is_available(self) -> bool:
        return self.status == VehicleStatus.AVAILABLE
    
    @property
    def has_space(self) -> bool:
        return self.available_capacity_tons > 0.5
    
    def add_load(self, weight_tons: float) -> bool:
        if weight_tons <= self.available_capacity_tons:
            self.current_load_tons += weight_tons
            return True
        return False
    
    def remove_load(self, weight_tons: float) -> None:
        self.current_load_tons = max(0, self.current_load_tons - weight_tons)


class VehicleLocation(Base):
    """Vehicle location history for tracking."""
    
    __tablename__ = "vehicle_locations"
    
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False, index=True)
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    speed_kmh = Column(Float, nullable=True)
    heading_degrees = Column(Float, nullable=True)
    recorded_at = Column(String(30), nullable=False)
    network_status = Column(String(20), default="online")
    
    vehicle = relationship("Vehicle", back_populates="location_history")
