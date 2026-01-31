from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

from app.models.checkpoint import CheckpointType
from app.schemas.mission import GeoPoint


# Toll charges by vehicle type
class TollCharges(BaseModel):
    """Toll charges for different vehicle types."""
    mini_truck: float = 0
    lcv: float = 0
    icv: float = 0
    mcv: float = 0
    hcv: float = 0
    mav: float = 0
    trailer: float = 0
    container: float = 0


# Average delays by time of day
class AvgDelays(BaseModel):
    """Average delays in minutes by time of day."""
    morning: int = 10   # 6AM - 10AM
    day: int = 5        # 10AM - 4PM
    evening: int = 15   # 4PM - 9PM
    night: int = 5      # 9PM - 6AM


# Operating hours
class OperatingHours(BaseModel):
    """Operating hours configuration."""
    open_24x7: bool = True
    open_time: str = "00:00"
    close_time: str = "23:59"


# No-entry timings
class NoEntryTimings(BaseModel):
    """No-entry timing restrictions for trucks."""
    enabled: bool = False
    restricted_start: str = ""
    restricted_end: str = ""
    vehicle_types: List[str] = []
    notes: str = ""


# Amenities
class Amenities(BaseModel):
    """Available amenities at checkpoint."""
    fuel_station: bool = False
    rest_area: bool = False
    food_court: bool = False
    parking: bool = False
    repair_shop: bool = False


# Checkpoint schemas
class CheckpointCreate(BaseModel):
    """Schema for creating checkpoint."""
    name: str = Field(..., max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    checkpoint_type: CheckpointType
    
    # Location
    location: GeoPoint
    highway_name: Optional[str] = None
    state: str = Field(..., max_length=50)
    district: Optional[str] = None
    
    # Toll
    toll_charges: Optional[TollCharges] = None
    fastag_enabled: bool = True
    
    # Delays
    avg_delays: Optional[AvgDelays] = None
    
    # Hours
    operating_hours: Optional[OperatingHours] = None
    no_entry_timings: Optional[NoEntryTimings] = None
    
    # Amenities
    amenities: Optional[Amenities] = None
    
    # Contact
    contact_number: Optional[str] = None


class CheckpointUpdate(BaseModel):
    """Schema for updating checkpoint."""
    name: Optional[str] = None
    is_active: Optional[bool] = None
    toll_charges: Optional[TollCharges] = None
    fastag_enabled: Optional[bool] = None
    avg_delays: Optional[AvgDelays] = None
    operating_hours: Optional[OperatingHours] = None
    no_entry_timings: Optional[NoEntryTimings] = None
    amenities: Optional[Amenities] = None
    contact_number: Optional[str] = None


class CheckpointResponse(BaseModel):
    """Checkpoint response schema."""
    id: UUID
    name: str
    code: Optional[str] = None
    checkpoint_type: CheckpointType
    
    # Location
    latitude: float
    longitude: float
    highway_name: Optional[str] = None
    state: str
    district: Optional[str] = None
    
    # Status
    is_active: bool
    
    # Toll
    toll_charges: TollCharges
    fastag_enabled: bool
    
    # Delays
    avg_delays: AvgDelays
    
    # Hours
    operating_hours: OperatingHours
    no_entry_timings: NoEntryTimings
    
    # Amenities
    amenities: Amenities
    
    # Contact
    contact_number: Optional[str] = None
    
    # Computed
    is_toll: bool
    has_no_entry: bool
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class CheckpointBrief(BaseModel):
    """Brief checkpoint info for lists and maps."""
    id: UUID
    name: str
    checkpoint_type: CheckpointType
    latitude: float
    longitude: float
    state: str
    is_toll: bool
    has_no_entry: bool
    
    class Config:
        from_attributes = True


# Search and filtering
class CheckpointSearchParams(BaseModel):
    """Parameters for checkpoint search."""
    # Location
    lat: Optional[float] = None
    lng: Optional[float] = None
    radius_km: float = 100
    
    # Filters
    checkpoint_types: Optional[List[CheckpointType]] = None
    states: Optional[List[str]] = None
    highway_name: Optional[str] = None
    has_fuel: Optional[bool] = None
    has_rest_area: Optional[bool] = None
    is_active: bool = True
    
    # Pagination
    page: int = 1
    page_size: int = 50


# Route checkpoint analysis - Module 1
class RouteCheckpoint(BaseModel):
    """Checkpoint along a route with timing."""
    checkpoint: CheckpointBrief
    sequence: int
    distance_from_origin_km: float
    estimated_arrival: str
    toll_amount: float
    expected_delay_minutes: int
    is_restricted_at_eta: bool  # No-entry applies at ETA


class RouteCheckpointAnalysis(BaseModel):
    """Full checkpoint analysis for a route."""
    total_checkpoints: int
    total_tolls: int
    total_toll_cost: float
    total_expected_delay_minutes: int
    restricted_checkpoints: int
    checkpoints: List[RouteCheckpoint]


# Delay estimation
class DelayEstimateRequest(BaseModel):
    """Request for delay estimation."""
    checkpoint_id: UUID
    arrival_time: str
    vehicle_type: str


class DelayEstimateResponse(BaseModel):
    """Response with delay estimation."""
    checkpoint_id: UUID
    checkpoint_name: str
    arrival_time: str
    estimated_delay_minutes: int
    toll_amount: float
    is_restricted: bool
    restriction_notes: Optional[str] = None
