from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_MakePoint, ST_SetSRID

from app.db import get_db
from app.models import Mission, MissionStatus, User, Vehicle, Waypoint
from app.schemas import (
    MissionCreate,
    MissionUpdate,
    MissionResponse,
    MissionBrief,
    GeoPoint,
)
from app.core import get_current_user, get_current_fleet_operator, get_current_driver
from datetime import datetime
import uuid as uuid_lib

router = APIRouter(prefix="/missions", tags=["Missions"])


def generate_mission_number() -> str:
    """Generate unique mission number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    unique_part = uuid_lib.uuid4().hex[:6].upper()
    return f"MSN-{timestamp}-{unique_part}"


def create_point(lat: float, lng: float):
    """Create PostGIS point from coordinates."""
    return func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)


@router.post("/", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
def create_mission(
    data: MissionCreate,
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """
    Create a new mission (fleet operator only).
    
    Module 1: Context-Aware Mission Planner
    - Creates mission with origin/destination
    - Assigns vehicle and driver if provided
    """
    # Validate vehicle if provided
    if data.vehicle_id:
        vehicle = db.query(Vehicle).filter(
            Vehicle.id == data.vehicle_id,
            Vehicle.owner_id == current_user.id,
        ).first()
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehicle not found or not owned by you",
            )
    
    # Validate driver if provided
    if data.driver_id:
        driver = db.query(User).filter(User.id == data.driver_id).first()
        if not driver or not driver.is_driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver not found",
            )
    
    # Create mission
    mission = Mission(
        mission_number=generate_mission_number(),
        operator_id=current_user.id,
        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id,
        origin=create_point(data.origin.latitude, data.origin.longitude),
        origin_address=data.origin_address,
        origin_city=data.origin_city,
        destination=create_point(data.destination.latitude, data.destination.longitude),
        destination_address=data.destination_address,
        destination_city=data.destination_city,
        planned_start=data.planned_start,
        cargo_type=data.cargo_type,
        cargo_description=data.cargo_description,
        weight_tons=data.weight_tons,
        notes=data.notes,
        status=MissionStatus.DRAFT,
    )
    
    # Set agent config if provided
    if data.agent_config:
        mission.agent_config = data.agent_config.model_dump()
    
    db.add(mission)
    db.commit()
    db.refresh(mission)
    
    # Create waypoints if provided
    if data.waypoints:
        for wp_data in data.waypoints:
            waypoint = Waypoint(
                mission_id=mission.id,
                sequence=wp_data.sequence,
                location=create_point(wp_data.location.latitude, wp_data.location.longitude),
                address=wp_data.address,
                waypoint_type=wp_data.waypoint_type,
                eta=wp_data.eta,
                notes=wp_data.notes,
                checkpoint_name=wp_data.checkpoint_name,
            )
            db.add(waypoint)
        db.commit()
        db.refresh(mission)
    
    return mission


@router.get("/", response_model=List[MissionBrief])
def list_missions(
    status: Optional[MissionStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List missions for current user.
    
    - Fleet operators see their operated missions
    - Drivers see their assigned missions
    """
    query = db.query(Mission)
    
    if current_user.is_fleet_operator:
        query = query.filter(Mission.operator_id == current_user.id)
    elif current_user.is_driver:
        query = query.filter(Mission.driver_id == current_user.id)
    else:
        # Admin can see all
        pass
    
    if status:
        query = query.filter(Mission.status == status)
    
    missions = query.order_by(Mission.created_at.desc()).offset(skip).limit(limit).all()
    return missions


@router.get("/{mission_id}", response_model=MissionResponse)
def get_mission(
    mission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get mission details."""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found",
        )
    
    # Check access
    if not current_user.is_admin:
        if current_user.is_fleet_operator and mission.operator_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if current_user.is_driver and mission.driver_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return mission


@router.patch("/{mission_id}", response_model=MissionResponse)
def update_mission(
    mission_id: UUID,
    data: MissionUpdate,
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """Update mission (fleet operator only)."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.operator_id == current_user.id,
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found",
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if field == "agent_config" and value:
            setattr(mission, field, value.model_dump() if hasattr(value, 'model_dump') else value)
        else:
            setattr(mission, field, value)
    
    db.commit()
    db.refresh(mission)
    
    return mission


@router.post("/{mission_id}/start", response_model=MissionResponse)
def start_mission(
    mission_id: UUID,
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db),
):
    """Start mission (driver only)."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.driver_id == current_user.id,
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found or not assigned to you",
        )
    
    if mission.status not in [MissionStatus.PLANNED, MissionStatus.ASSIGNED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start mission in {mission.status} status",
        )
    
    mission.status = MissionStatus.EN_ROUTE_PICKUP
    mission.actual_start = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(mission)
    
    return mission


@router.post("/{mission_id}/complete", response_model=MissionResponse)
def complete_mission(
    mission_id: UUID,
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db),
):
    """Complete mission (driver only)."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.driver_id == current_user.id,
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found or not assigned to you",
        )
    
    if mission.status != MissionStatus.AT_DELIVERY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mission must be at delivery location to complete",
        )
    
    mission.status = MissionStatus.COMPLETED
    mission.actual_end = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(mission)
    
    return mission


@router.post("/{mission_id}/cancel", response_model=MissionResponse)
def cancel_mission(
    mission_id: UUID,
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """Cancel mission (fleet operator only)."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.operator_id == current_user.id,
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found",
        )
    
    if mission.status == MissionStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed mission",
        )
    
    mission.status = MissionStatus.CANCELLED
    
    db.commit()
    db.refresh(mission)
    
    return mission


@router.post("/{mission_id}/update-status", response_model=MissionResponse)
def update_mission_status(
    mission_id: UUID,
    new_status: MissionStatus,
    current_user: User = Depends(get_current_driver),
    db: Session = Depends(get_db),
):
    """Update mission status (driver only)."""
    mission = db.query(Mission).filter(
        Mission.id == mission_id,
        Mission.driver_id == current_user.id,
    ).first()
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission not found or not assigned to you",
        )
    
    # Validate status transition
    valid_transitions = {
        MissionStatus.EN_ROUTE_PICKUP: [MissionStatus.AT_PICKUP],
        MissionStatus.AT_PICKUP: [MissionStatus.LOADING],
        MissionStatus.LOADING: [MissionStatus.IN_TRANSIT],
        MissionStatus.IN_TRANSIT: [MissionStatus.AT_DELIVERY],
        MissionStatus.AT_DELIVERY: [MissionStatus.UNLOADING],
        MissionStatus.UNLOADING: [MissionStatus.COMPLETED],
    }
    
    if mission.status not in valid_transitions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update status from {mission.status}",
        )
    
    if new_status not in valid_transitions.get(mission.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from {mission.status} to {new_status}",
        )
    
    mission.status = new_status
    
    if new_status == MissionStatus.COMPLETED:
        mission.actual_end = datetime.utcnow().isoformat()
    
    db.commit()
    db.refresh(mission)
    
    return mission
