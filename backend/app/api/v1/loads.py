from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_Transform

from app.db import get_db
from app.models import Load, LoadStatus, Mission, MissionLoad, User, Vehicle
from app.schemas import (
    LoadCreate,
    LoadUpdate,
    LoadResponse,
    LoadBrief,
    LoadSearchParams,
    LoadMatchRequest,
    LoadMatchResponse,
    BackhaulSearchRequest,
    BackhaulSearchResponse,
    BackhaulSuggestion,
)
from app.core import get_current_user
from datetime import datetime

router = APIRouter(prefix="/loads", tags=["Loads"])


def create_point(lat: float, lng: float):
    """Create PostGIS point from coordinates."""
    return func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)


@router.post("/", response_model=LoadResponse, status_code=status.HTTP_201_CREATED)
def create_load(
    data: LoadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Post a new load/freight for matching.
    """
    load = Load(
        shipper_id=str(current_user.id),
        shipper_name=data.shipper_name,
        shipper_phone=data.shipper_phone,
        cargo_type=data.cargo_type,
        description=data.description,
        weight_tons=data.weight_tons,
        volume_cbm=data.volume_cbm,
        pickup_location=create_point(data.pickup_location.latitude, data.pickup_location.longitude),
        pickup_address=data.pickup_address,
        pickup_city=data.pickup_city,
        pickup_window_start=data.pickup_window_start,
        pickup_window_end=data.pickup_window_end,
        delivery_location=create_point(data.delivery_location.latitude, data.delivery_location.longitude),
        delivery_address=data.delivery_address,
        delivery_city=data.delivery_city,
        delivery_window_start=data.delivery_window_start,
        delivery_window_end=data.delivery_window_end,
        offered_rate=data.offered_rate,
        rate_type=data.rate_type,
        negotiable=data.negotiable,
        requires_cover=data.requires_cover,
        requires_crane=data.requires_crane,
        special_instructions=data.special_instructions,
        posted_at=datetime.utcnow().isoformat(),
        expires_at=data.expires_at,
        status=LoadStatus.POSTED,
    )
    
    db.add(load)
    db.commit()
    db.refresh(load)
    
    return load


@router.get("/", response_model=List[LoadBrief])
def list_loads(
    status_filter: Optional[LoadStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List loads (available or user's posted loads).
    """
    query = db.query(Load)
    
    if status_filter:
        query = query.filter(Load.status == status_filter)
    else:
        # Default to showing available loads
        query = query.filter(Load.status == LoadStatus.POSTED)
    
    loads = query.order_by(Load.posted_at.desc()).offset(skip).limit(limit).all()
    return loads


@router.post("/search", response_model=List[LoadBrief])
def search_loads(
    params: LoadSearchParams,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search loads with spatial and other filters.
    
    Module 3: Dynamic Capacity Manager
    - Search by pickup/delivery location radius
    - Filter by cargo type, weight, rate
    """
    query = db.query(Load).filter(Load.status == LoadStatus.POSTED)
    
    # Spatial filter - pickup location
    if params.pickup_lat and params.pickup_lng:
        pickup_point = create_point(params.pickup_lat, params.pickup_lng)
        # Convert radius from km to meters for ST_DWithin
        query = query.filter(
            func.ST_DWithin(
                Load.pickup_location,
                pickup_point,
                params.pickup_radius_km * 1000,  # Convert to meters
                True  # Use spheroid for accuracy
            )
        )
    
    # Spatial filter - delivery location
    if params.delivery_lat and params.delivery_lng:
        delivery_point = create_point(params.delivery_lat, params.delivery_lng)
        query = query.filter(
            func.ST_DWithin(
                Load.delivery_location,
                delivery_point,
                params.delivery_radius_km * 1000,
                True
            )
        )
    
    # Cargo type filter
    if params.cargo_types:
        query = query.filter(Load.cargo_type.in_(params.cargo_types))
    
    # Weight filters
    if params.min_weight:
        query = query.filter(Load.weight_tons >= params.min_weight)
    if params.max_weight:
        query = query.filter(Load.weight_tons <= params.max_weight)
    
    # Rate filters
    if params.min_rate:
        query = query.filter(Load.offered_rate >= params.min_rate)
    if params.max_rate:
        query = query.filter(Load.offered_rate <= params.max_rate)
    
    # Pagination
    offset = (params.page - 1) * params.page_size
    loads = query.order_by(Load.posted_at.desc()).offset(offset).limit(params.page_size).all()
    
    return loads


@router.get("/{load_id}", response_model=LoadResponse)
def get_load(
    load_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get load details.
    """
    load = db.query(Load).filter(Load.id == load_id).first()
    
    if not load:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Load not found",
        )
    
    return load


@router.patch("/{load_id}", response_model=LoadResponse)
def update_load(
    load_id: UUID,
    data: LoadUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update load details.
    """
    load = db.query(Load).filter(
        Load.id == load_id,
        Load.shipper_id == str(current_user.id),
    ).first()
    
    if not load:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Load not found or not owned by you",
        )
    
    if load.status != LoadStatus.POSTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update posted loads",
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(load, field, value)
    
    db.commit()
    db.refresh(load)
    
    return load


@router.post("/{load_id}/match", response_model=LoadMatchResponse)
def match_load_to_mission(
    load_id: UUID,
    mission_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Match a load to a mission (LTL pooling).
    
    Module 3: Dynamic Capacity Manager
    """
    # Get load
    load = db.query(Load).filter(Load.id == load_id).first()
    if not load:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Load not found")
    
    if load.status != LoadStatus.POSTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Load is not available")
    
    # Get mission
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    
    # Check if mission has vehicle with capacity
    if not mission.vehicle_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mission has no assigned vehicle",
        )
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == mission.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    # Check capacity
    if load.weight_tons > vehicle.available_capacity_tons:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient vehicle capacity. Available: {vehicle.available_capacity_tons} tons",
        )
    
    # Create mission-load link
    mission_load = MissionLoad(
        mission_id=mission_id,
        load_id=load_id,
        pickup_sequence=len(mission.loads) * 2 + 1,
        delivery_sequence=len(mission.loads) * 2 + 2,
        fare_portion=load.offered_rate,
    )
    db.add(mission_load)
    
    # Update load status
    load.status = LoadStatus.MATCHED
    load.matched_mission_id = mission_id
    
    # Update vehicle load
    vehicle.add_load(load.weight_tons)
    
    db.commit()
    
    return LoadMatchResponse(
        success=True,
        message="Load matched successfully",
        load_id=load_id,
        mission_id=mission_id,
        fare_amount=load.offered_rate,
        pickup_sequence=mission_load.pickup_sequence,
        delivery_sequence=mission_load.delivery_sequence,
    )


@router.post("/{load_id}/cancel", response_model=LoadResponse)
def cancel_load(
    load_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a posted load.
    """
    load = db.query(Load).filter(
        Load.id == load_id,
        Load.shipper_id == str(current_user.id),
    ).first()
    
    if not load:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Load not found or not owned by you",
        )
    
    if load.status not in [LoadStatus.POSTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel posted loads",
        )
    
    load.status = LoadStatus.CANCELLED
    
    db.commit()
    db.refresh(load)
    
    return load


@router.post("/backhaul/search", response_model=BackhaulSearchResponse)
def search_backhaul_loads(
    params: BackhaulSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for backhaul loads near mission destination.
    
    Module 3: Dynamic Capacity Manager
    - Finds loads near current/upcoming destination
    - Calculates detour and cost-benefit
    """
    # Get mission
    mission = db.query(Mission).filter(Mission.id == params.mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    
    # Search for loads near destination
    destination_city = mission.destination_city or "Unknown"
    
    # Find loads with pickup near mission destination
    query = db.query(Load).filter(Load.status == LoadStatus.POSTED)
    
    # Spatial filter - pickup near destination
    query = query.filter(
        func.ST_DWithin(
            Load.pickup_location,
            mission.destination,
            params.max_detour_km * 1000,  # Convert to meters
            True
        )
    )
    
    # Filter by minimum revenue
    if params.min_revenue > 0:
        query = query.filter(Load.offered_rate >= params.min_revenue)
    
    loads = query.limit(10).all()
    
    # Build suggestions with scoring
    suggestions = []
    for load in loads:
        # Calculate simple detour estimate (in real app, use routing API)
        detour_km = 10.0  # Placeholder - would calculate actual distance
        detour_minutes = int(detour_km * 2)  # Rough estimate
        
        # Skip if exceeds max detour
        if detour_km > params.max_detour_km or detour_minutes > params.max_detour_minutes:
            continue
        
        # Cost-benefit calculation
        fuel_cost_per_km = 8.0  # INR per km estimate
        additional_fuel_cost = detour_km * fuel_cost_per_km * 2  # Round trip
        net_benefit = load.offered_rate - additional_fuel_cost
        
        # Score based on net benefit and detour
        match_score = min(100, max(0, 50 + (net_benefit / 100) - (detour_km * 2)))
        
        # Recommendation based on score
        if match_score >= 70:
            recommendation = "highly_recommended"
        elif match_score >= 50:
            recommendation = "recommended"
        else:
            recommendation = "marginal"
        
        suggestions.append(BackhaulSuggestion(
            load=LoadBrief(
                id=load.id,
                cargo_type=load.cargo_type,
                weight_tons=load.weight_tons,
                pickup_city=load.pickup_city,
                delivery_city=load.delivery_city,
                offered_rate=load.offered_rate,
                display_rate=load.display_rate,
                status=load.status,
                is_ltl=load.is_ltl,
            ),
            detour_km=detour_km,
            detour_minutes=detour_minutes,
            potential_revenue=load.offered_rate,
            additional_fuel_cost=additional_fuel_cost,
            net_benefit=net_benefit,
            match_score=match_score,
            recommendation=recommendation,
        ))
    
    # Sort by match score
    suggestions.sort(key=lambda x: x.match_score, reverse=True)
    
    return BackhaulSearchResponse(
        mission_id=params.mission_id,
        current_destination_city=destination_city,
        suggestions=suggestions,
        total_found=len(suggestions),
    )
