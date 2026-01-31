from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.mission import MissionStatus, PaymentStatus, WaypointType


# Location helper
class GeoPoint(BaseModel):
    """Geographic point."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


# Waypoint schemas
class WaypointCreate(BaseModel):
    """Schema for creating waypoint."""
    sequence: int = Field(..., ge=0)
    location: GeoPoint
    address: Optional[str] = None
    waypoint_type: WaypointType
    eta: Optional[str] = None
    notes: Optional[str] = None
    checkpoint_name: Optional[str] = None


class WaypointResponse(BaseModel):
    """Waypoint response."""
    id: UUID
    sequence: int
    latitude: float
    longitude: float
    address: Optional[str] = None
    waypoint_type: WaypointType
    eta: Optional[str] = None
    actual_arrival: Optional[str] = None
    actual_departure: Optional[str] = None
    estimated_delay_minutes: Optional[float] = None
    
    class Config:
        from_attributes = True


# Route data
class RouteData(BaseModel):
    """Route information from maps API."""
    polyline: str = ""
    distance_km: float = 0
    duration_minutes: float = 0
    steps: List[dict] = []


# Fare breakdown - Module 1 output
class FareBreakdown(BaseModel):
    """Detailed fare breakdown."""
    base: float = 0
    distance_charge: float = 0
    fuel_surcharge: float = 0
    toll_charges: float = 0
    loading_charges: float = 0
    difficulty_premium: float = 0
    total: float = 0
    currency: str = "INR"


# Risk assessment - Module 1 output
class ETARange(BaseModel):
    """ETA range predictions."""
    optimistic: str = ""
    realistic: str = ""
    pessimistic: str = ""


class RiskFactor(BaseModel):
    """Individual risk factor."""
    name: str
    severity: str  # low, medium, high
    description: str
    impact_minutes: Optional[int] = None


class RiskAssessment(BaseModel):
    """Risk assessment for mission."""
    overall_score: float = Field(..., ge=0, le=100)
    factors: List[RiskFactor] = []
    eta_range: ETARange


# Agent config
class AgentConfig(BaseModel):
    """Agent configuration for mission."""
    enabled: bool = True
    max_detour_km: float = 30
    max_detour_minutes: int = 45
    auto_accept_threshold: float = Field(0.8, ge=0, le=1)


# Mission schemas
class MissionCreate(BaseModel):
    """Schema for creating a mission."""
    # Origin
    origin: GeoPoint
    origin_address: str = Field(..., max_length=500)
    origin_city: Optional[str] = None
    
    # Destination
    destination: GeoPoint
    destination_address: str = Field(..., max_length=500)
    destination_city: Optional[str] = None
    
    # Assignment
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    
    # Timing
    planned_start: Optional[str] = None
    
    # Cargo
    cargo_type: Optional[str] = None
    cargo_description: Optional[str] = None
    weight_tons: Optional[float] = None
    
    # Agent
    agent_config: Optional[AgentConfig] = None
    
    # Waypoints
    waypoints: Optional[List[WaypointCreate]] = None
    
    notes: Optional[str] = None


class MissionUpdate(BaseModel):
    """Schema for updating mission."""
    status: Optional[MissionStatus] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    planned_start: Optional[str] = None
    notes: Optional[str] = None
    agent_config: Optional[AgentConfig] = None


class MissionResponse(BaseModel):
    """Mission response schema."""
    id: UUID
    mission_number: str
    
    # Participants
    operator_id: UUID
    driver_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    
    # Status
    status: MissionStatus
    
    # Locations
    origin_address: str
    origin_city: Optional[str] = None
    destination_address: str
    destination_city: Optional[str] = None
    
    # Route
    route_data: Optional[RouteData] = None
    distance_km: float
    
    # Timing
    planned_start: Optional[str] = None
    actual_start: Optional[str] = None
    estimated_end: Optional[str] = None
    actual_end: Optional[str] = None
    
    # Fare
    quoted_fare: Optional[FareBreakdown] = None
    total_fare: float
    payment_status: PaymentStatus
    
    # Risk
    risk_assessment: Optional[RiskAssessment] = None
    
    # Cargo
    cargo_type: Optional[str] = None
    weight_tons: Optional[float] = None
    
    # Waypoints
    waypoints: List[WaypointResponse] = []
    
    # Flags
    is_active: bool
    is_completed: bool
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class MissionBrief(BaseModel):
    """Brief mission info for lists."""
    id: UUID
    mission_number: str
    status: MissionStatus
    origin_city: Optional[str] = None
    destination_city: Optional[str] = None
    distance_km: float
    total_fare: float
    
    class Config:
        from_attributes = True


# Mission planning request - Module 1 input
class MissionPlanRequest(BaseModel):
    """Request for mission planning (Module 1)."""
    origin: GeoPoint
    origin_address: str
    destination: GeoPoint
    destination_address: str
    vehicle_type: str
    cargo_type: Optional[str] = None
    weight_tons: Optional[float] = None
    planned_start: Optional[str] = None


# Mission planning response - Module 1 output
class MissionPlanResponse(BaseModel):
    """Response from mission planning (Module 1)."""
    route_data: RouteData
    fare_breakdown: FareBreakdown
    risk_assessment: RiskAssessment
    waypoints: List[WaypointCreate]
    estimated_duration_hours: float
    recommended_departure: Optional[str] = None
