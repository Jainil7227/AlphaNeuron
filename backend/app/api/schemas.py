"""
Pydantic Schemas for API Request/Response Models

All data structures for the Neuro-Logistics API.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==========================================
# ENUMS
# ==========================================

class MissionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class DecisionAction(str, Enum):
    CONTINUE = "CONTINUE"
    REROUTE = "REROUTE"
    STOP = "STOP"
    ALERT = "ALERT"


# ==========================================
# MODULE 1: MISSION PLANNER
# ==========================================

class PlanMissionRequest(BaseModel):
    """Request to plan a new mission."""
    origin: str = Field(..., description="Starting city", example="Mumbai")
    destination: str = Field(..., description="Destination city", example="Delhi")
    cargo_type: str = Field(..., description="Type of cargo", example="Electronics")
    weight_tons: float = Field(..., ge=0.1, le=30, description="Cargo weight in tons", example=15.0)
    vehicle_id: Optional[str] = Field(None, description="Specific vehicle ID to use")


class StartMissionRequest(BaseModel):
    """Request to start a planned mission."""
    vehicle_id: str = Field(..., description="Vehicle ID to assign")


class ETARange(BaseModel):
    """ETA range with optimistic/expected/pessimistic estimates."""
    optimistic: Dict[str, Any]
    expected: Dict[str, Any]
    pessimistic: Dict[str, Any]


class RouteInfo(BaseModel):
    """Route information."""
    distance_km: float
    highways: List[str]
    toll_plazas: int
    toll_cost: float
    checkpoints: List[str]
    fuel_stops: int
    is_estimated: bool = False


class FareBreakdown(BaseModel):
    """Fare calculation breakdown."""
    base_fare: float
    effort_multiplier: float
    adjusted_base: float
    toll_cost: float
    fuel_estimate: float
    driver_allowance: float
    total_fare: float
    per_km_rate: float


class RiskAssessment(BaseModel):
    """Risk assessment for a mission."""
    score: int
    level: RiskLevel
    factors: List[str]
    recommendations: List[str]


class MissionPlan(BaseModel):
    """Complete mission plan."""
    origin: str
    destination: str
    cargo: Dict[str, Any]
    route: Dict[str, Any]
    eta_range: Dict[str, Any]
    fare: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    ai_insights: Dict[str, Any]
    return_load_options: List[Dict[str, Any]]
    created_at: str


# ==========================================
# MODULE 2: DECISION ENGINE
# ==========================================

class EvaluateSituationRequest(BaseModel):
    """Request to evaluate current situation."""
    mission_id: str = Field(..., description="Active mission ID")
    current_location: str = Field(..., description="Current city/location")
    conditions: Optional[Dict[str, Any]] = Field(
        None, 
        description="Current conditions (traffic, weather, etc.)"
    )


class EvaluateOpportunityRequest(BaseModel):
    """Request to evaluate a specific opportunity."""
    mission_id: str = Field(..., description="Active mission ID")
    opportunity: Dict[str, Any] = Field(
        ..., 
        description="Opportunity details (load, reroute, etc.)"
    )


class RerouteRequest(BaseModel):
    """Request for reroute options."""
    mission_id: str = Field(..., description="Active mission ID")
    reason: str = Field("traffic", description="Reason for rerouting")


class CopilotChatRequest(BaseModel):
    """Request for AI copilot chat."""
    mission_id: str = Field(..., description="Active mission ID")
    query: str = Field(..., description="User's question or request")
    context: Optional[Dict[str, Any]] = Field(
        None, 
        description="Additional context (location, conditions, etc.)"
    )


class DecisionResult(BaseModel):
    """Result of a decision evaluation."""
    mission_id: str
    observation: Dict[str, Any]
    ai_analysis: Dict[str, Any]
    decision: Dict[str, Any]
    timestamp: str


# ==========================================
# MODULE 3: CAPACITY MANAGER
# ==========================================

class FindLTLRequest(BaseModel):
    """Request to find LTL loads for pooling."""
    mission_id: str = Field(..., description="Active mission ID")


class FindBackhaulRequest(BaseModel):
    """Request to find backhaul options."""
    mission_id: str = Field(..., description="Active mission ID")
    home_base: Optional[str] = Field(None, description="Home base city (defaults to origin)")


class AcceptLoadRequest(BaseModel):
    """Request to accept an LTL load."""
    mission_id: str = Field(..., description="Active mission ID")
    load_id: str = Field(..., description="Load ID to accept")


class BookBackhaulRequest(BaseModel):
    """Request to book a backhaul load."""
    mission_id: str = Field(..., description="Active mission ID")
    load_id: str = Field(..., description="Backhaul load ID to book")


class CapacityInfo(BaseModel):
    """Capacity information."""
    total_tons: float
    current_load_tons: float
    available_tons: float
    utilization_percent: float


# ==========================================
# COMMON RESPONSES
# ==========================================

class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str


class ErrorResponse(BaseModel):
    """Generic error response."""
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    modules: Dict[str, str]


# ==========================================
# DATA RESPONSES
# ==========================================

class RoutesResponse(BaseModel):
    """Available routes response."""
    cities: List[str]
    popular_routes: List[Dict[str, Any]]


class MissionResponse(BaseModel):
    """Mission details response."""
    id: str
    status: str
    origin: str
    destination: str
    cargo: Dict[str, Any]
    route: Dict[str, Any]
    progress_percent: float
    created_at: str
    started_at: Optional[str]


class VehicleResponse(BaseModel):
    """Vehicle details response."""
    id: str
    registration: str
    type: str
    capacity_tons: float
    current_load_tons: float
    driver_name: str
    current_city: str
    status: str


class DemoScenario(BaseModel):
    """Demo scenario data."""
    scenario_name: str
    description: str
    mission: Dict[str, Any]
    vehicle: Dict[str, Any]
    sample_conditions: Dict[str, Any]
    available_opportunities: List[Dict[str, Any]]
