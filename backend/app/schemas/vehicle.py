from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from app.models.vehicle import VehicleType, VehicleStatus, FuelType


# Location schemas
class LocationUpdate(BaseModel):
    """Schema for location update."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed_kmh: Optional[float] = Field(None, ge=0)
    heading_degrees: Optional[float] = Field(None, ge=0, le=360)


class LocationResponse(BaseModel):
    """Location response with coordinates."""
    latitude: float
    longitude: float
    last_updated: Optional[str] = None


# Vehicle schemas
class VehicleBase(BaseModel):
    """Base vehicle schema."""
    registration_number: str = Field(..., pattern=r"^[A-Z]{2}[0-9]{2}[A-Z]{1,2}[0-9]{4}$")
    vehicle_type: VehicleType
    make: str = Field(..., max_length=50)
    model: str = Field(..., max_length=50)
    year: int = Field(..., ge=2000, le=2030)


class VehicleCreate(VehicleBase):
    """Schema for vehicle registration."""
    # Capacity
    max_capacity_tons: float = Field(..., gt=0)
    volume_capacity_cbm: Optional[float] = Field(None, gt=0)
    
    # Dimensions
    dimensions: Optional[dict] = None
    
    # Fuel
    fuel_type: FuelType = FuelType.DIESEL
    tank_capacity_liters: Optional[float] = None
    avg_fuel_efficiency: Optional[float] = None
    
    # Indian compliance
    insurance_expiry: Optional[date] = None
    fitness_expiry: Optional[date] = None
    permit_type: Optional[str] = None
    permit_states: Optional[List[str]] = None
    permit_expiry: Optional[date] = None
    puc_expiry: Optional[date] = None


class VehicleUpdate(BaseModel):
    """Schema for vehicle update."""
    make: Optional[str] = None
    model: Optional[str] = None
    
    # Status
    status: Optional[VehicleStatus] = None
    
    # Capacity
    max_capacity_tons: Optional[float] = None
    current_load_tons: Optional[float] = None
    volume_capacity_cbm: Optional[float] = None
    current_volume_cbm: Optional[float] = None
    
    # Fuel
    fuel_type: Optional[FuelType] = None
    fuel_level_percent: Optional[float] = Field(None, ge=0, le=100)
    tank_capacity_liters: Optional[float] = None
    avg_fuel_efficiency: Optional[float] = None
    
    # Compliance
    insurance_expiry: Optional[date] = None
    fitness_expiry: Optional[date] = None
    permit_type: Optional[str] = None
    permit_states: Optional[List[str]] = None
    permit_expiry: Optional[date] = None
    puc_expiry: Optional[date] = None
    
    # Assignment
    assigned_driver_id: Optional[UUID] = None
    
    # Images
    images: Optional[List[str]] = None


class VehicleResponse(VehicleBase):
    """Vehicle response schema."""
    id: UUID
    owner_id: UUID
    status: VehicleStatus
    
    # Capacity
    max_capacity_tons: float
    current_load_tons: float
    volume_capacity_cbm: Optional[float] = None
    current_volume_cbm: float
    
    # Computed
    available_capacity_tons: float
    capacity_utilization_percent: float
    
    # Location
    current_location: Optional[LocationResponse] = None
    last_location_update: Optional[str] = None
    
    # Fuel
    fuel_type: FuelType
    fuel_level_percent: float
    
    # Compliance
    insurance_expiry: Optional[date] = None
    fitness_expiry: Optional[date] = None
    permit_type: Optional[str] = None
    permit_states: Optional[List[str]] = None
    
    # Assignment
    assigned_driver_id: Optional[UUID] = None
    current_mission_id: Optional[UUID] = None
    
    # Stats
    total_trips: int
    total_km: float
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class VehicleBrief(BaseModel):
    """Brief vehicle info for lists."""
    id: UUID
    registration_number: str
    vehicle_type: VehicleType
    status: VehicleStatus
    available_capacity_tons: float
    
    class Config:
        from_attributes = True


# Capacity management
class LoadCapacityUpdate(BaseModel):
    """Schema for updating load capacity."""
    weight_tons: float = Field(..., gt=0)
    operation: str = Field(..., pattern="^(add|remove)$")


class CapacityResponse(BaseModel):
    """Capacity status response."""
    vehicle_id: UUID
    max_capacity_tons: float
    current_load_tons: float
    available_capacity_tons: float
    utilization_percent: float
    has_space: bool


# Fleet overview
class FleetStats(BaseModel):
    """Fleet statistics."""
    total_vehicles: int
    available_vehicles: int
    on_mission_vehicles: int
    maintenance_vehicles: int
    total_capacity_tons: float
    utilized_capacity_tons: float
    avg_utilization_percent: float
