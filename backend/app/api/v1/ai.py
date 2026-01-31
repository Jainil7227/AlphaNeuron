from typing import Dict, Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Mission, User
from app.core import get_current_user
from app.services.ai.grok_client import get_grok_client, GrokClient

router = APIRouter(prefix="/ai", tags=["AI"])


class MissionAnalysisRequest(BaseModel):
    """Request for mission analysis."""
    origin: str
    destination: str
    cargo_type: str
    weight_tons: float
    vehicle_type: str


class OpportunityEvaluationRequest(BaseModel):
    """Request for opportunity evaluation."""
    mission_id: UUID
    opportunity_type: str
    opportunity_details: Dict[str, Any]


class BackhaulRequest(BaseModel):
    """Request for backhaul suggestion."""
    current_location: str
    destination: str
    vehicle_capacity: float
    available_loads: List[Dict[str, Any]]


@router.post("/analyze-mission")
async def analyze_mission(
    request: MissionAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    """
    AI-powered mission analysis.
    
    Module 1: Context-Aware Mission Planner
    """
    try:
        client = get_grok_client()
        result = await client.analyze_mission(
            origin=request.origin,
            destination=request.destination,
            cargo_type=request.cargo_type,
            weight_tons=request.weight_tons,
            vehicle_type=request.vehicle_type,
        )
        return {"success": True, "analysis": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/evaluate-opportunity")
async def evaluate_opportunity(
    request: OpportunityEvaluationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    AI-powered opportunity evaluation.
    
    Module 2: Rolling Decision Engine
    """
    # Get mission context
    mission = db.query(Mission).filter(Mission.id == request.mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    
    mission_context = {
        "origin": mission.origin_address,
        "destination": mission.destination_address,
        "status": mission.status.value,
        "cargo_type": mission.cargo_type,
        "weight_tons": mission.weight_tons,
    }
    
    try:
        client = get_grok_client()
        result = await client.evaluate_opportunity(
            mission_context=mission_context,
            opportunity=request.opportunity_details,
        )
        return {"success": True, "evaluation": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/suggest-backhaul")
async def suggest_backhaul(
    request: BackhaulRequest,
    current_user: User = Depends(get_current_user),
):
    """
    AI-powered backhaul suggestion.
    
    Module 3: Dynamic Capacity Manager
    """
    try:
        client = get_grok_client()
        result = await client.suggest_backhaul(
            current_location=request.current_location,
            destination=request.destination,
            vehicle_capacity=request.vehicle_capacity,
            available_loads=request.available_loads,
        )
        return {"success": True, "suggestion": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
