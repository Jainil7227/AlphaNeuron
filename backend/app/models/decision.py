from sqlalchemy import Column, String, Float, Enum, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class DecisionType(str, enum.Enum):
    """Type of agent decision."""
    REROUTE = "reroute"
    LOAD_MATCH = "load_match"
    BACKHAUL = "backhaul"
    REFUEL = "refuel"
    REST_STOP = "rest_stop"
    DELAY_ALERT = "delay_alert"
    SPEED_ADVISORY = "speed_advisory"


class DecisionStatus(str, enum.Enum):
    """Status of decision."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AUTO_ACCEPTED = "auto_accepted"
    EXPIRED = "expired"
    EXECUTED = "executed"


class AgentDecision(Base):
    """
    Records AI agent decisions during mission.
    
    Module 2: Rolling Decision Engine
    - Continuous monitoring loop
    - Opportunity detection
    - Cost-benefit analysis
    - Decision execution tracking
    """
    
    # Link to mission
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False, index=True)
    
    # Decision classification
    decision_type = Column(Enum(DecisionType), nullable=False, index=True)
    status = Column(Enum(DecisionStatus), default=DecisionStatus.PENDING, nullable=False, index=True)
    
    # Trigger info
    trigger_reason = Column(String(200), nullable=False)
    triggered_at = Column(String(30), nullable=False)
    
    # Opportunity details
    opportunity = Column(JSONB, default=lambda: {
        "description": "",
        "source": "",
        "valid_until": "",
    })
    
    # Cost-Benefit Analysis
    cost_benefit = Column(JSONB, default=lambda: {
        "potential_revenue": 0,
        "additional_cost": 0,
        "time_cost_minutes": 0,
        "distance_cost_km": 0,
        "net_benefit": 0,
        "confidence_score": 0,
    })
    
    # Recommendation
    recommendation = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    auto_acceptable = Column(Boolean, default=False)
    
    # Proposed changes
    proposed_changes = Column(JSONB, default=lambda: {
        "new_route": None,
        "new_waypoints": [],
        "fare_adjustment": 0,
        "eta_change_minutes": 0,
    })
    
    # Decision outcome
    decided_at = Column(String(30), nullable=True)
    decided_by = Column(String(50), nullable=True)  # "agent", "driver", "operator"
    rejection_reason = Column(Text, nullable=True)
    
    # Execution tracking
    executed_at = Column(String(30), nullable=True)
    execution_result = Column(JSONB, nullable=True)
    
    # Actual outcome (for learning)
    actual_outcome = Column(JSONB, nullable=True)
    
    # Link to load if LOAD_MATCH or BACKHAUL
    related_load_id = Column(UUID(as_uuid=True), ForeignKey("loads.id"), nullable=True)
    
    # Relationships
    mission = relationship("Mission", back_populates="decisions")
    
    # Properties
    @property
    def is_pending(self) -> bool:
        return self.status == DecisionStatus.PENDING
    
    @property
    def was_accepted(self) -> bool:
        return self.status in [DecisionStatus.ACCEPTED, DecisionStatus.AUTO_ACCEPTED, DecisionStatus.EXECUTED]
    
    @property
    def net_benefit(self) -> float:
        return self.cost_benefit.get("net_benefit", 0) if self.cost_benefit else 0
    
    @property
    def is_profitable(self) -> bool:
        return self.net_benefit > 0
    
    def accept(self, decided_by: str = "driver") -> None:
        """Mark decision as accepted."""
        from datetime import datetime
        self.status = DecisionStatus.ACCEPTED
        self.decided_at = datetime.utcnow().isoformat()
        self.decided_by = decided_by
    
    def reject(self, reason: str, decided_by: str = "driver") -> None:
        """Mark decision as rejected."""
        from datetime import datetime
        self.status = DecisionStatus.REJECTED
        self.decided_at = datetime.utcnow().isoformat()
        self.decided_by = decided_by
        self.rejection_reason = reason
    
    def mark_executed(self, result: dict = None) -> None:
        """Mark decision as executed."""
        from datetime import datetime
        self.status = DecisionStatus.EXECUTED
        self.executed_at = datetime.utcnow().isoformat()
        self.execution_result = result
