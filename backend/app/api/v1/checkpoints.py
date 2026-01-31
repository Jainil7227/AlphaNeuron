from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models import Checkpoint, CheckpointType, User
from app.schemas import (
    CheckpointCreate,
    CheckpointUpdate,
    CheckpointResponse,
    CheckpointBrief,
    CheckpointSearchParams,
    RouteCheckpoint,
    RouteCheckpointAnalysis,
    DelayEstimateRequest,
    DelayEstimateResponse,
)
from app.core import get_current_user, get_current_admin
from datetime import datetime

router = APIRouter(prefix="/checkpoints", tags=["Checkpoints"])


def create_point(lat: float, lng: float):
    """Create PostGIS point from coordinates."""
    return func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)


@router.post("/", response_model=CheckpointResponse, status_code=status.HTTP_201_CREATED)
def create_checkpoint(
    data: CheckpointCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Create a new checkpoint (admin only).
    
    Module 1: Context-Aware Mission Planner
    - Toll plazas, checkpoints for route planning
    """
    checkpoint = Checkpoint(
        name=data.name,
        code=data.code,
        checkpoint_type=data.checkpoint_type,
        location=create_point(data.location.latitude, data.location.longitude),
        highway_name=data.highway_name,
        state=data.state,
        district=data.district,
        toll_charges=data.toll_charges.model_dump() if data.toll_charges else {},
        fastag_enabled=data.fastag_enabled,
        avg_delays=data.avg_delays.model_dump() if data.avg_delays else {},
        operating_hours=data.operating_hours.model_dump() if data.operating_hours else {},
        no_entry_timings=data.no_entry_timings.model_dump() if data.no_entry_timings else {},
        amenities=data.amenities.model_dump() if data.amenities else {},
        contact_number=data.contact_number,
        is_active=True,
    )
    
    db.add(checkpoint)
    db.commit()
    db.refresh(checkpoint)
    
    return checkpoint


@router.get("/", response_model=List[CheckpointBrief])
def list_checkpoints(
    checkpoint_type: Optional[CheckpointType] = None,
    state: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List checkpoints with filters.
    """
    query = db.query(Checkpoint).filter(Checkpoint.is_active == True)
    
    if checkpoint_type:
        query = query.filter(Checkpoint.checkpoint_type == checkpoint_type)
    
    if state:
        query = query.filter(Checkpoint.state == state)
    
    checkpoints = query.order_by(Checkpoint.name).offset(skip).limit(limit).all()
    return checkpoints


@router.post("/search", response_model=List[CheckpointBrief])
def search_checkpoints(
    params: CheckpointSearchParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search checkpoints with spatial and other filters.
    """
    query = db.query(Checkpoint)
    
    if params.is_active:
        query = query.filter(Checkpoint.is_active == True)
    
    # Spatial filter
    if params.lat and params.lng:
        center_point = create_point(params.lat, params.lng)
        query = query.filter(
            func.ST_DWithin(
                Checkpoint.location,
                center_point,
                params.radius_km * 1000,  # Convert to meters
                True
            )
        )
    
    # Type filter
    if params.checkpoint_types:
        query = query.filter(Checkpoint.checkpoint_type.in_(params.checkpoint_types))
    
    # State filter
    if params.states:
        query = query.filter(Checkpoint.state.in_(params.states))
    
    # Highway filter
    if params.highway_name:
        query = query.filter(Checkpoint.highway_name.ilike(f"%{params.highway_name}%"))
    
    # Amenity filters
    if params.has_fuel:
        query = query.filter(Checkpoint.amenities["fuel_station"].astext == "true")
    
    if params.has_rest_area:
        query = query.filter(Checkpoint.amenities["rest_area"].astext == "true")
    
    # Pagination
    offset = (params.page - 1) * params.page_size
    checkpoints = query.order_by(Checkpoint.name).offset(offset).limit(params.page_size).all()
    
    return checkpoints


@router.get("/{checkpoint_id}", response_model=CheckpointResponse)
def get_checkpoint(
    checkpoint_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get checkpoint details.
    """
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    
    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found",
        )
    
    return checkpoint


@router.patch("/{checkpoint_id}", response_model=CheckpointResponse)
def update_checkpoint(
    checkpoint_id: UUID,
    data: CheckpointUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Update checkpoint (admin only).
    """
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == checkpoint_id).first()
    
    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found",
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            if hasattr(value, 'model_dump'):
                setattr(checkpoint, field, value.model_dump())
            else:
                setattr(checkpoint, field, value)
    
    db.commit()
    db.refresh(checkpoint)
    
    return checkpoint


@router.post("/delay-estimate", response_model=DelayEstimateResponse)
def estimate_delay(
    data: DelayEstimateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Estimate delay at a checkpoint for given arrival time.
    
    Module 1: Context-Aware Mission Planner
    """
    checkpoint = db.query(Checkpoint).filter(Checkpoint.id == data.checkpoint_id).first()
    
    if not checkpoint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Checkpoint not found",
        )
    
    # Get delay based on time of day
    delay_minutes = checkpoint.get_delay_for_time(data.arrival_time)
    
    # Get toll amount for vehicle type
    toll_amount = checkpoint.get_toll_for_vehicle(data.vehicle_type)
    
    # Check if restricted at arrival time
    is_restricted = not checkpoint.is_operating_at(data.arrival_time)
    
    restriction_notes = None
    if is_restricted:
        no_entry = checkpoint.no_entry_timings or {}
        if no_entry.get("enabled"):
            restriction_notes = f"No entry from {no_entry.get('restricted_start')} to {no_entry.get('restricted_end')}"
    
    return DelayEstimateResponse(
        checkpoint_id=checkpoint.id,
        checkpoint_name=checkpoint.name,
        arrival_time=data.arrival_time,
        estimated_delay_minutes=delay_minutes,
        toll_amount=toll_amount,
        is_restricted=is_restricted,
        restriction_notes=restriction_notes,
    )


@router.get("/tolls/by-state/{state}", response_model=List[CheckpointBrief])
def get_tolls_by_state(
    state: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all toll plazas in a state.
    """
    checkpoints = db.query(Checkpoint).filter(
        Checkpoint.state == state,
        Checkpoint.checkpoint_type == CheckpointType.TOLL_PLAZA,
        Checkpoint.is_active == True,
    ).order_by(Checkpoint.name).all()
    
    return checkpoints


@router.get("/highway/{highway_name}", response_model=List[CheckpointBrief])
def get_checkpoints_on_highway(
    highway_name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get all checkpoints on a highway.
    """
    checkpoints = db.query(Checkpoint).filter(
        Checkpoint.highway_name.ilike(f"%{highway_name}%"),
        Checkpoint.is_active == True,
    ).order_by(Checkpoint.name).all()
    
    return checkpoints
