from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db import get_db
from app.models import Vehicle, VehicleStatus, VehicleLocation, User
from app.schemas import (
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
    VehicleBrief,
    LocationUpdate,
    CapacityResponse,
    FleetStats,
)
from app.core import get_current_user, get_current_fleet_operator
from datetime import datetime

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


def create_point(lat: float, lng: float):
    """Create PostGIS point from coordinates."""
    return func.ST_SetSRID(func.ST_MakePoint(lng, lat), 4326)


@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    data: VehicleCreate,
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """
    Register a new vehicle (fleet operator only).
    """
    # Check registration number uniqueness
    existing = db.query(Vehicle).filter(
        Vehicle.registration_number == data.registration_number
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle with this registration number already exists",
        )
    
    vehicle = Vehicle(
        owner_id=current_user.id,
        registration_number=data.registration_number,
        vehicle_type=data.vehicle_type,
        make=data.make,
        model=data.model,
        year=data.year,
        max_capacity_tons=data.max_capacity_tons,
        volume_capacity_cbm=data.volume_capacity_cbm,
        dimensions=data.dimensions,
        fuel_type=data.fuel_type,
        tank_capacity_liters=data.tank_capacity_liters,
        avg_fuel_efficiency=data.avg_fuel_efficiency,
        insurance_expiry=data.insurance_expiry,
        fitness_expiry=data.fitness_expiry,
        permit_type=data.permit_type,
        permit_states=data.permit_states or [],
        permit_expiry=data.permit_expiry,
        puc_expiry=data.puc_expiry,
        status=VehicleStatus.AVAILABLE,
    )
    
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.get("/", response_model=List[VehicleBrief])
def list_vehicles(
    status_filter: Optional[VehicleStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """
    List vehicles owned by current user.
    """
    query = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id)
    
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    vehicles = query.order_by(Vehicle.created_at.desc()).offset(skip).limit(limit).all()
    return vehicles


@router.get("/stats", response_model=FleetStats)
def get_fleet_stats(
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """
    Get fleet statistics for dashboard.
    """
    vehicles = db.query(Vehicle).filter(Vehicle.owner_id == current_user.id).all()
    
    total = len(vehicles)
    available = sum(1 for v in vehicles if v.status == VehicleStatus.AVAILABLE)
    on_mission = sum(1 for v in vehicles if v.status == VehicleStatus.ON_MISSION)
    maintenance = sum(1 for v in vehicles if v.status == VehicleStatus.MAINTENANCE)
    
    total_capacity = sum(v.max_capacity_tons for v in vehicles)
    utilized_capacity = sum(v.current_load_tons for v in vehicles)
    
    avg_utilization = (utilized_capacity / total_capacity * 100) if total_capacity > 0 else 0
    
    return FleetStats(
        total_vehicles=total,
        available_vehicles=available,
        on_mission_vehicles=on_mission,
        maintenance_vehicles=maintenance,
        total_capacity_tons=total_capacity,
        utilized_capacity_tons=utilized_capacity,
        avg_utilization_percent=round(avg_utilization, 2),
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """
    Get vehicle details.
    """
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.owner_id == current_user.id,
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    data: VehicleUpdate,
    current_user: User = Depends(get_current_fleet_operator),
    db: Session = Depends(get_db),
):
    """
    Update vehicle details.
    """
    vehicle = db.query(Vehicle).filter(
        Vehicle.id == vehicle_id,
        Vehicle.owner_id == current_user.id,
    ).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(vehicle, field, value)
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.post("/{vehicle_id}/location", response_model=VehicleResponse)
def update_vehicle_location(
    vehicle_id: UUID,
    data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update vehicle location (driver or system).
    
    Also stores in location history.
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    # Check access - owner or assigned driver
    if not current_user.is_admin:
        if vehicle.owner_id != current_user.id and vehicle.assigned_driver_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )
    
    # Update current location
    now = datetime.utcnow().isoformat()
    vehicle.current_location = create_point(data.latitude, data.longitude)
    vehicle.last_location_update = now
    
    # Store in history
    location_record = VehicleLocation(
        vehicle_id=vehicle_id,
        location=create_point(data.latitude, data.longitude),
        speed_kmh=data.speed_kmh,
        heading_degrees=data.heading_degrees,
        recorded_at=now,
    )
    db.add(location_record)
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.get("/{vehicle_id}/capacity", response_model=CapacityResponse)
def get_vehicle_capacity(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get vehicle capacity status (for LTL operations).
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    return CapacityResponse(
        vehicle_id=vehicle.id,
        max_capacity_tons=vehicle.max_capacity_tons,
        current_load_tons=vehicle.current_load_tons,
        available_capacity_tons=vehicle.available_capacity_tons,
        utilization_percent=vehicle.capacity_utilization_percent,
        has_space=vehicle.has_space,
    )


@router.post("/{vehicle_id}/add-load", response_model=CapacityResponse)
def add_load_to_vehicle(
    vehicle_id: UUID,
    weight_tons: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Add load to vehicle (LTL pooling).
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    if not vehicle.add_load(weight_tons):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient capacity. Available: {vehicle.available_capacity_tons} tons",
        )
    
    db.commit()
    db.refresh(vehicle)
    
    return CapacityResponse(
        vehicle_id=vehicle.id,
        max_capacity_tons=vehicle.max_capacity_tons,
        current_load_tons=vehicle.current_load_tons,
        available_capacity_tons=vehicle.available_capacity_tons,
        utilization_percent=vehicle.capacity_utilization_percent,
        has_space=vehicle.has_space,
    )


@router.post("/{vehicle_id}/remove-load", response_model=CapacityResponse)
def remove_load_from_vehicle(
    vehicle_id: UUID,
    weight_tons: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remove load from vehicle (after delivery).
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    
    vehicle.remove_load(weight_tons)
    
    db.commit()
    db.refresh(vehicle)
    
    return CapacityResponse(
        vehicle_id=vehicle.id,
        max_capacity_tons=vehicle.max_capacity_tons,
        current_load_tons=vehicle.current_load_tons,
        available_capacity_tons=vehicle.available_capacity_tons,
        utilization_percent=vehicle.capacity_utilization_percent,
        has_space=vehicle.has_space,
    )
