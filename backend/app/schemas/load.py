from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.load import LoadStatus, CargoType, RateType
from app.schemas.mission import GeoPoint


# Load schemas
class LoadBase(BaseModel):
    """Base load schema."""
    shipper_name: str = Field(..., max_length=100)
    shipper_phone: str = Field(..., pattern=r"^[6-9]\d{9}$")
    
    # Cargo
    cargo_type: CargoType = CargoType.GENERAL
    description: Optional[str] = None
    weight_tons: float = Field(..., gt=0, le=50)
    volume_cbm: Optional[float] = Field(None, gt=0)
    
    # Pricing
    offered_rate: float = Field(..., gt=0)
    rate_type: RateType = RateType.FIXED
    negotiable: bool = True


class LoadCreate(LoadBase):
    """Schema for posting a load."""
    # Pickup
    pickup_location: GeoPoint
    pickup_address: str = Field(..., max_length=500)
    pickup_city: str = Field(..., max_length=100)
    pickup_window_start: str
    pickup_window_end: str
    
    # Delivery
    delivery_location: GeoPoint
    delivery_address: str = Field(..., max_length=500)
    delivery_city: str = Field(..., max_length=100)
    delivery_window_start: Optional[str] = None
    delivery_window_end: Optional[str] = None
    
    # Special requirements
    requires_cover: bool = False
    requires_crane: bool = False
    special_instructions: Optional[str] = None
    
    # Expiry
    expires_at: Optional[str] = None


class LoadUpdate(BaseModel):
    """Schema for updating load."""
    description: Optional[str] = None
    offered_rate: Optional[float] = None
    negotiable: Optional[bool] = None
    pickup_window_start: Optional[str] = None
    pickup_window_end: Optional[str] = None
    delivery_window_start: Optional[str] = None
    delivery_window_end: Optional[str] = None
    special_instructions: Optional[str] = None
    expires_at: Optional[str] = None


class LoadResponse(LoadBase):
    """Load response schema."""
    id: UUID
    status: LoadStatus
    
    # Shipper
    shipper_id: Optional[str] = None
    shipper_rating: float
    
    # Pickup
    pickup_address: str
    pickup_city: str
    pickup_latitude: float
    pickup_longitude: float
    pickup_window_start: str
    pickup_window_end: str
    
    # Delivery
    delivery_address: str
    delivery_city: str
    delivery_latitude: float
    delivery_longitude: float
    delivery_window_start: Optional[str] = None
    delivery_window_end: Optional[str] = None
    
    # Special
    requires_cover: bool
    requires_crane: bool
    special_instructions: Optional[str] = None
    
    # Matching
    matched_mission_id: Optional[UUID] = None
    
    # Timing
    posted_at: str
    expires_at: Optional[str] = None
    
    # Computed
    is_available: bool
    is_ltl: bool
    display_rate: str
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoadBrief(BaseModel):
    """Brief load info for lists."""
    id: UUID
    cargo_type: CargoType
    weight_tons: float
    pickup_city: str
    delivery_city: str
    offered_rate: float
    display_rate: str
    status: LoadStatus
    is_ltl: bool
    
    class Config:
        from_attributes = True


# Search and filtering
class LoadSearchParams(BaseModel):
    """Parameters for load search."""
    # Location filters
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    pickup_radius_km: float = 50
    
    delivery_lat: Optional[float] = None
    delivery_lng: Optional[float] = None
    delivery_radius_km: float = 50
    
    # Cargo filters
    cargo_types: Optional[List[CargoType]] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    
    # Rate filters
    min_rate: Optional[float] = None
    max_rate: Optional[float] = None
    
    # Time filters
    pickup_after: Optional[str] = None
    pickup_before: Optional[str] = None
    
    # Pagination
    page: int = 1
    page_size: int = 20


# Load matching - Module 3
class LoadMatchRequest(BaseModel):
    """Request to match load to mission."""
    load_id: UUID
    mission_id: UUID
    proposed_fare: Optional[float] = None


class LoadMatchResponse(BaseModel):
    """Response from load matching."""
    success: bool
    message: str
    load_id: UUID
    mission_id: UUID
    fare_amount: Optional[float] = None
    pickup_sequence: Optional[int] = None
    delivery_sequence: Optional[int] = None


# Backhaul suggestion - Module 3
class BackhaulSuggestion(BaseModel):
    """Backhaul load suggestion."""
    load: LoadBrief
    
    # Distance analysis
    detour_km: float
    detour_minutes: int
    
    # Cost-benefit
    potential_revenue: float
    additional_fuel_cost: float
    net_benefit: float
    
    # Scoring
    match_score: float = Field(..., ge=0, le=100)
    recommendation: str  # "highly_recommended", "recommended", "marginal"


class BackhaulSearchRequest(BaseModel):
    """Request for backhaul search."""
    mission_id: UUID
    max_detour_km: float = 50
    max_detour_minutes: int = 60
    min_revenue: float = 0


class BackhaulSearchResponse(BaseModel):
    """Response with backhaul suggestions."""
    mission_id: UUID
    current_destination_city: str
    suggestions: List[BackhaulSuggestion]
    total_found: int
