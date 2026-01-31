from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import AgentDecision, DecisionStatus, DecisionType, Mission, User
from app.schemas import (
    DecisionResponse,
    DecisionBrief,
    DecisionAccept,
    DecisionReject,
    AgentAlert,
    MissionDecisionHistory,
    AgentMetrics,
)
from app.core import get_current_user, get_current_driver
from datetime import datetime

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.get("/decisions/{mission_id}", response_model=List[DecisionBrief])
def get_mission_decisions(
    mission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all agent decisions for a mission.
    """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    
    # Check access
    if not current_user.is_admin:
        if mission.operator_id != current_user.id and mission.driver_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    decisions = db.query(AgentDecision).filter(
        AgentDecision.mission_id == mission_id
    ).order_by(AgentDecision.created_at.desc()).all()
    
    return decisions


@router.get("/decisions/{mission_id}/pending", response_model=List[DecisionResponse])
def get_pending_decisions(
    mission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get pending agent decisions for a mission.
    
    Module 2: Rolling Decision Engine
    - Returns decisions awaiting driver/operator response
    """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    
    # Check access
    if not current_user.is_admin:
        if mission.operator_id != current_user.id and mission.driver_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    decisions = db.query(AgentDecision).filter(
        AgentDecision.mission_id == mission_id,
        AgentDecision.status == DecisionStatus.PENDING,
    ).order_by(AgentDecision.triggered_at.desc()).all()
    
    return decisions


@router.get("/decision/{decision_id}", response_model=DecisionResponse)
def get_decision(
    decision_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get agent decision details.
    """
    decision = db.query(AgentDecision).filter(AgentDecision.id == decision_id).first()
    
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    
    # Check access via mission
    mission = db.query(Mission).filter(Mission.id == decision.mission_id).first()
    if not current_user.is_admin:
        if mission.operator_id != current_user.id and mission.driver_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return decision


@router.post("/decision/{decision_id}/accept", response_model=DecisionResponse)
def accept_decision(
    decision_id: UUID,
    data: DecisionAccept,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Accept an agent decision.
    
    Module 2: Rolling Decision Engine
    - Driver or operator accepts the recommendation
    - Triggers execution of proposed changes
    """
    decision = db.query(AgentDecision).filter(AgentDecision.id == decision_id).first()
    
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    
    if decision.status != DecisionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decision is already {decision.status.value}",
        )
    
    # Check access
    mission = db.query(Mission).filter(Mission.id == decision.mission_id).first()
    if not current_user.is_admin:
        if mission.operator_id != current_user.id and mission.driver_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Accept the decision
    decision.status = DecisionStatus.ACCEPTED
    decision.decided_at = datetime.utcnow().isoformat()
    decision.decided_by = data.decided_by
    
    db.commit()
    db.refresh(decision)
    
    # TODO: Trigger execution of proposed changes (route update, load match, etc.)
    
    return decision


@router.post("/decision/{decision_id}/reject", response_model=DecisionResponse)
def reject_decision(
    decision_id: UUID,
    data: DecisionReject,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reject an agent decision.
    """
    decision = db.query(AgentDecision).filter(AgentDecision.id == decision_id).first()
    
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision not found")
    
    if decision.status != DecisionStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Decision is already {decision.status.value}",
        )
    
    # Check access
    mission = db.query(Mission).filter(Mission.id == decision.mission_id).first()
    if not current_user.is_admin:
        if mission.operator_id != current_user.id and mission.driver_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    # Reject the decision
    decision.status = DecisionStatus.REJECTED
    decision.decided_at = datetime.utcnow().isoformat()
    decision.decided_by = data.decided_by
    decision.rejection_reason = data.rejection_reason
    
    db.commit()
    db.refresh(decision)
    
    return decision


@router.get("/history/{mission_id}", response_model=MissionDecisionHistory)
def get_decision_history(
    mission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get complete decision history for a mission.
    """
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    
    # Check access
    if not current_user.is_admin:
        if mission.operator_id != current_user.id and mission.driver_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    decisions = db.query(AgentDecision).filter(
        AgentDecision.mission_id == mission_id
    ).order_by(AgentDecision.created_at.desc()).all()
    
    total = len(decisions)
    accepted = sum(1 for d in decisions if d.status in [DecisionStatus.ACCEPTED, DecisionStatus.AUTO_ACCEPTED, DecisionStatus.EXECUTED])
    rejected = sum(1 for d in decisions if d.status == DecisionStatus.REJECTED)
    pending = sum(1 for d in decisions if d.status == DecisionStatus.PENDING)
    
    # Calculate total benefit from accepted decisions
    total_benefit = sum(
        d.cost_benefit.get("net_benefit", 0) if d.cost_benefit else 0
        for d in decisions
        if d.status in [DecisionStatus.ACCEPTED, DecisionStatus.AUTO_ACCEPTED, DecisionStatus.EXECUTED]
    )
    
    return MissionDecisionHistory(
        mission_id=mission_id,
        total_decisions=total,
        accepted_count=accepted,
        rejected_count=rejected,
        pending_count=pending,
        total_benefit_realized=total_benefit,
        decisions=decisions,
    )


@router.get("/metrics", response_model=AgentMetrics)
def get_agent_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get agent performance metrics for dashboard.
    """
    # Get missions for current user
    if current_user.is_fleet_operator:
        mission_ids = db.query(Mission.id).filter(Mission.operator_id == current_user.id).subquery()
    elif current_user.is_driver:
        mission_ids = db.query(Mission.id).filter(Mission.driver_id == current_user.id).subquery()
    else:
        # Admin sees all
        mission_ids = db.query(Mission.id).subquery()
    
    decisions = db.query(AgentDecision).filter(
        AgentDecision.mission_id.in_(mission_ids)
    ).all()
    
    total = len(decisions)
    if total == 0:
        return AgentMetrics(
            total_decisions=0,
            acceptance_rate=0,
            avg_confidence_score=0,
            total_revenue_generated=0,
            total_cost_saved=0,
            avg_response_time_seconds=0,
        )
    
    accepted = sum(1 for d in decisions if d.was_accepted)
    acceptance_rate = (accepted / total * 100) if total > 0 else 0
    
    avg_confidence = sum(d.confidence_score for d in decisions) / total
    
    # Revenue from accepted decisions
    total_revenue = sum(
        d.cost_benefit.get("potential_revenue", 0) if d.cost_benefit else 0
        for d in decisions
        if d.was_accepted
    )
    
    # Cost saved
    total_cost_saved = sum(
        d.cost_benefit.get("net_benefit", 0) if d.cost_benefit else 0
        for d in decisions
        if d.was_accepted
    )
    
    # Average response time (simplified)
    response_times = []
    for d in decisions:
        if d.decided_at and d.triggered_at:
            # Would calculate actual time difference
            response_times.append(30)  # Placeholder 30 seconds
    avg_response = sum(response_times) / len(response_times) if response_times else 0
    
    return AgentMetrics(
        total_decisions=total,
        acceptance_rate=round(acceptance_rate, 2),
        avg_confidence_score=round(avg_confidence, 3),
        total_revenue_generated=total_revenue,
        total_cost_saved=total_cost_saved,
        avg_response_time_seconds=avg_response,
    )
