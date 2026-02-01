"""
Maps API endpoints with mock data for Indian cities.

Replaces Google Maps API for demo/hackathon purposes.
Provides:
- Route calculation between cities
- Fare estimation
- Toll and checkpoint information
- Fuel stop locations
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from app.services.maps import get_maps_service

router = APIRouter(prefix="/maps", tags=["Maps"])


# Request/Response Models
class RouteRequest(BaseModel):
    """Request for route calculation."""
    origin: str = Field(..., description="Origin city name", example="Delhi")
    destination: str = Field(..., description="Destination city name", example="Mumbai")


class FareRequest(BaseModel):
    """Request for fare calculation."""
    distance_km: float = Field(..., gt=0, description="Distance in kilometers")
    weight_tons: float = Field(..., ge=0, description="Cargo weight in tons")
    vehicle_type: str = Field("hcv", description="Vehicle type")
    toll_cost: float = Field(0, ge=0, description="Total toll cost")


class CityInfo(BaseModel):
    """City information response."""
    city: str
    latitude: float
    longitude: float


# Endpoints
@router.get("/cities", summary="Get supported cities")
def get_supported_cities():
    """
    Get list of all supported cities for route planning.
    
    Returns alphabetically sorted list of city names.
    """
    service = get_maps_service()
    cities = service.get_supported_cities()
    return {
        "cities": cities,
        "total": len(cities),
        "note": "Use these city names in route calculations",
    }


@router.get("/routes", summary="Get pre-defined routes")
def get_supported_routes():
    """
    Get list of pre-defined routes with accurate distance and toll data.
    
    These routes have detailed toll plaza, fuel stop, and checkpoint information.
    """
    service = get_maps_service()
    routes = service.get_supported_routes()
    return {
        "routes": routes,
        "total": len(routes),
        "note": "Routes not in this list will use estimated calculations",
    }


@router.post("/route", summary="Calculate route")
def calculate_route(request: RouteRequest):
    """
    Calculate route between two cities.
    
    Returns:
    - Distance and duration
    - Toll plazas with costs
    - Fuel stops along the route
    - State border checkpoints
    - Polyline for map display
    """
    service = get_maps_service()
    
    try:
        route = service.get_route(request.origin, request.destination)
        
        # Calculate total toll cost
        total_toll = sum(toll["cost"] for toll in route.tolls)
        
        # Convert toll locations to serializable format
        tolls_serialized = []
        for toll in route.tolls:
            toll_copy = toll.copy()
            if hasattr(toll_copy.get("location"), "model_dump"):
                toll_copy["location"] = toll_copy["location"].model_dump()
            tolls_serialized.append(toll_copy)
        
        # Convert fuel stop locations
        fuel_stops_serialized = []
        for stop in route.fuel_stops:
            stop_copy = stop.copy()
            if hasattr(stop_copy.get("location"), "model_dump"):
                stop_copy["location"] = stop_copy["location"].model_dump()
            fuel_stops_serialized.append(stop_copy)
        
        # Convert checkpoint locations
        checkpoints_serialized = []
        for cp in route.checkpoints:
            cp_copy = cp.copy()
            if hasattr(cp_copy.get("location"), "model_dump"):
                cp_copy["location"] = cp_copy["location"].model_dump()
            checkpoints_serialized.append(cp_copy)
        
        return {
            "success": True,
            "route": {
                "origin": route.origin,
                "destination": route.destination,
                "distance_km": route.distance_km,
                "duration_hours": route.duration_hours,
                "duration_display": f"{int(route.duration_hours)}h {int((route.duration_hours % 1) * 60)}m",
                "polyline": route.polyline,
                "is_estimated": route.is_estimated,
            },
            "tolls": {
                "plazas": tolls_serialized,
                "total_count": len(route.tolls),
                "total_cost": total_toll,
            },
            "fuel_stops": fuel_stops_serialized,
            "checkpoints": checkpoints_serialized,
            "highways": route.highways,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/fare", summary="Calculate fare")
def calculate_fare(request: FareRequest):
    """
    Calculate freight fare for a route.
    
    Uses industry-standard rates for Indian road freight:
    - Base rate per km
    - Weight multiplier
    - Toll costs
    - Fuel surcharge
    """
    service = get_maps_service()
    
    fare = service.calculate_fare(
        distance_km=request.distance_km,
        weight_tons=request.weight_tons,
        vehicle_type=request.vehicle_type,
        toll_cost=request.toll_cost,
    )
    
    return {
        "success": True,
        "fare": fare,
    }


@router.get("/city/{city_name}", summary="Get city coordinates")
def get_city_coordinates(city_name: str):
    """
    Get coordinates for a city.
    
    Returns latitude and longitude for map display.
    """
    service = get_maps_service()
    
    try:
        point = service.get_city_location(city_name)
        return {
            "success": True,
            "city": city_name,
            "location": point.model_dump(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/distance", summary="Get distance between cities")
def get_distance(
    origin: str = Query(..., description="Origin city"),
    destination: str = Query(..., description="Destination city"),
):
    """
    Get distance between two cities.
    
    Quick lookup without full route details.
    """
    service = get_maps_service()
    
    try:
        route = service.get_route(origin, destination)
        return {
            "success": True,
            "origin": origin,
            "destination": destination,
            "distance_km": route.distance_km,
            "duration_hours": route.duration_hours,
            "is_estimated": route.is_estimated,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/toll-estimate", summary="Estimate toll costs")
def estimate_tolls(
    origin: str = Query(..., description="Origin city"),
    destination: str = Query(..., description="Destination city"),
    vehicle_type: str = Query("hcv", description="Vehicle type (lcv, hcv, mav)"),
):
    """
    Estimate toll costs for a route.
    
    Returns list of toll plazas and total cost.
    """
    service = get_maps_service()
    
    try:
        route = service.get_route(origin, destination)
        
        # Adjust tolls based on vehicle type
        multiplier = {"lcv": 0.6, "hcv": 1.0, "mav": 1.5}.get(vehicle_type.lower(), 1.0)
        
        tolls = []
        for toll in route.tolls:
            toll_copy = toll.copy()
            toll_copy["cost"] = round(toll["cost"] * multiplier, 2)
            if hasattr(toll_copy.get("location"), "model_dump"):
                toll_copy["location"] = toll_copy["location"].model_dump()
            tolls.append(toll_copy)
        
        total = sum(t["cost"] for t in tolls)
        
        return {
            "success": True,
            "origin": origin,
            "destination": destination,
            "vehicle_type": vehicle_type,
            "tolls": tolls,
            "total_cost": total,
            "is_estimated": route.is_estimated,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
