from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.decision import DecisionType, DecisionStatus


# Cost-benefit analysis
class CostBenefit(BaseModel):
    """Cost-benefit breakdown for decision."""
    potential_revenue: float = 0
    additional_cost: float = 0
    time_cost_minutes: int = 0
    distance_cost_km: float = 0
    net_benefit: float = 0
    confidence_score: float = Field(0, ge=0, le=1)


# Opportunity details
class Opportunity(BaseModel):
    """Details of detected opportunity."""
    description: str
    source: str  # "load_board", "backhaul_match", "fuel_price", "traffic"
    valid_until: str


# Proposed changes
class ProposedChanges(BaseModel):
    """Changes proposed by agent."""
    new_route: Optional[dict] = None
    new_waypoints: List[dict] = []
    fare_adjustment: float = 0
    eta_change_minutes: int = 0


# Decision schemas
class DecisionCreate(BaseModel):
    """Schema for creating agent decision (internal use)."""
    mission_id: UUID
    decision_type: DecisionType
    trigger_reason: str
    opportunity: Opportunity
    cost_benefit: CostBenefit
    recommendation: str
    confidence_score: float = Field(..., ge=0, le=1)
    auto_acceptable: bool = False
    proposed_changes: Optional[ProposedChanges] = None
    related_load_id: Optional[UUID] = None


class DecisionResponse(BaseModel):
    """Agent decision response."""
    id: UUID
    mission_id: UUID
    
    # Type and status
    decision_type: DecisionType
    status: DecisionStatus
    
    # Trigger
    trigger_reason: str
    triggered_at: str
    
    # Details
    opportunity: Opportunity
    cost_benefit: CostBenefit
    
    # Recommendation
    recommendation: str
    confidence_score: float
    auto_acceptable: bool
    
    # Changes
    proposed_changes: Optional[ProposedChanges] = None
    
    # Outcome
    decided_at: Optional[str] = None
    decided_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    # Execution
    executed_at: Optional[str] = None
    execution_result: Optional[dict] = None
    
    # Computed
    is_pending: bool
    was_accepted: bool
    net_benefit: float
    is_profitable: bool
    
    # Related
    related_load_id: Optional[UUID] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class DecisionBrief(BaseModel):
    """Brief decision info for lists."""
    id: UUID
    decision_type: DecisionType
    status: DecisionStatus
    recommendation: str
    net_benefit: float
    confidence_score: float
    triggered_at: str
    
    class Config:
        from_attributes = True


# Decision actions
class DecisionAccept(BaseModel):
    """Schema for accepting decision."""
    decided_by: str = "driver"  # "driver", "operator", "agent"


class DecisionReject(BaseModel):
    """Schema for rejecting decision."""
    rejection_reason: str = Field(..., min_length=5, max_length=500)
    decided_by: str = "driver"


# Agent alert for real-time notification
class AgentAlert(BaseModel):
    """Real-time alert from agent to driver/operator."""
    decision_id: UUID
    mission_id: UUID
    decision_type: DecisionType
    
    # Summary
    title: str
    message: str
    urgency: str  # "low", "medium", "high"
    
    # Quick stats
    net_benefit: float
    confidence_score: float
    expires_at: str
    
    # Action required
    auto_acceptable: bool
    requires_immediate_action: bool


# Decision history for mission
class MissionDecisionHistory(BaseModel):
    """Decision history for a mission."""
    mission_id: UUID
    total_decisions: int
    accepted_count: int
    rejected_count: int
    pending_count: int
    total_benefit_realized: float
    decisions: List[DecisionBrief]


# Agent performance metrics
class AgentMetrics(BaseModel):
    """Agent performance metrics."""
    total_decisions: int
    acceptance_rate: float
    avg_confidence_score: float
    total_revenue_generated: float
    total_cost_saved: float
    avg_response_time_seconds: float
