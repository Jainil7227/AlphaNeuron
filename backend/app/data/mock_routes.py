"""
Mock Indian Routes Data

Hardcoded route information for major Indian logistics corridors.
No Google Maps dependency - uses realistic estimates.
"""

from typing import Dict, Any, Optional
import random

# Major Indian logistics corridors with realistic data
INDIAN_ROUTES = {
    # North India
    ("Delhi", "Mumbai"): {
        "distance_km": 1420,
        "base_hours": 24,
        "highways": ["NH48", "Mumbai-Agra Expressway"],
        "tolls": 12,
        "toll_cost": 2800,
        "checkpoints": ["Rajasthan Border", "Gujarat Border", "Maharashtra Border"],
        "fuel_stops": 4,
        "risk_level": "medium",
    },
    ("Delhi", "Kolkata"): {
        "distance_km": 1530,
        "base_hours": 26,
        "highways": ["NH19", "NH2"],
        "tolls": 15,
        "toll_cost": 3200,
        "checkpoints": ["UP Border", "Bihar Border", "Jharkhand Border", "West Bengal Border"],
        "fuel_stops": 5,
        "risk_level": "medium",
    },
    ("Delhi", "Jaipur"): {
        "distance_km": 280,
        "base_hours": 5,
        "highways": ["NH48"],
        "tolls": 3,
        "toll_cost": 450,
        "checkpoints": ["Rajasthan Border"],
        "fuel_stops": 1,
        "risk_level": "low",
    },
    ("Delhi", "Chandigarh"): {
        "distance_km": 250,
        "base_hours": 4.5,
        "highways": ["NH44"],
        "tolls": 4,
        "toll_cost": 380,
        "checkpoints": ["Haryana Border", "Punjab Border"],
        "fuel_stops": 1,
        "risk_level": "low",
    },
    
    # West India
    ("Mumbai", "Pune"): {
        "distance_km": 150,
        "base_hours": 3,
        "highways": ["Mumbai-Pune Expressway"],
        "tolls": 2,
        "toll_cost": 350,
        "checkpoints": [],
        "fuel_stops": 0,
        "risk_level": "low",
    },
    ("Mumbai", "Ahmedabad"): {
        "distance_km": 530,
        "base_hours": 9,
        "highways": ["NH48"],
        "tolls": 6,
        "toll_cost": 1200,
        "checkpoints": ["Gujarat Border"],
        "fuel_stops": 2,
        "risk_level": "low",
    },
    ("Mumbai", "Bangalore"): {
        "distance_km": 980,
        "base_hours": 16,
        "highways": ["NH48", "NH44"],
        "tolls": 10,
        "toll_cost": 2100,
        "checkpoints": ["Karnataka Border"],
        "fuel_stops": 3,
        "risk_level": "medium",
    },
    
    # South India
    ("Bangalore", "Chennai"): {
        "distance_km": 350,
        "base_hours": 6,
        "highways": ["NH48"],
        "tolls": 4,
        "toll_cost": 650,
        "checkpoints": ["Tamil Nadu Border"],
        "fuel_stops": 1,
        "risk_level": "low",
    },
    ("Chennai", "Hyderabad"): {
        "distance_km": 630,
        "base_hours": 10,
        "highways": ["NH65"],
        "tolls": 7,
        "toll_cost": 1100,
        "checkpoints": ["Andhra Pradesh Border", "Telangana Border"],
        "fuel_stops": 2,
        "risk_level": "medium",
    },
    ("Bangalore", "Hyderabad"): {
        "distance_km": 570,
        "base_hours": 9,
        "highways": ["NH44"],
        "tolls": 6,
        "toll_cost": 950,
        "checkpoints": ["Telangana Border"],
        "fuel_stops": 2,
        "risk_level": "low",
    },
    
    # East India
    ("Kolkata", "Bhubaneswar"): {
        "distance_km": 440,
        "base_hours": 8,
        "highways": ["NH16"],
        "tolls": 5,
        "toll_cost": 750,
        "checkpoints": ["Odisha Border"],
        "fuel_stops": 2,
        "risk_level": "medium",
    },
    
    # Cross-country
    ("Mumbai", "Kolkata"): {
        "distance_km": 2050,
        "base_hours": 36,
        "highways": ["NH44", "NH6"],
        "tolls": 20,
        "toll_cost": 4500,
        "checkpoints": ["Maharashtra Border", "Madhya Pradesh Border", "Chhattisgarh Border", "Odisha Border", "West Bengal Border"],
        "fuel_stops": 6,
        "risk_level": "high",
    },
    ("Chennai", "Delhi"): {
        "distance_km": 2200,
        "base_hours": 38,
        "highways": ["NH44"],
        "tolls": 22,
        "toll_cost": 4800,
        "checkpoints": ["Andhra Pradesh Border", "Telangana Border", "Maharashtra Border", "Madhya Pradesh Border", "UP Border"],
        "fuel_stops": 7,
        "risk_level": "high",
    },
}


def get_route_info(origin: str, destination: str) -> Dict[str, Any]:
    """
    Get route information between two cities.
    
    Returns hardcoded data if available, otherwise estimates based on distance.
    """
    # Normalize city names
    origin = origin.strip().title()
    destination = destination.strip().title()
    
    # Try direct route
    key = (origin, destination)
    if key in INDIAN_ROUTES:
        route = INDIAN_ROUTES[key].copy()
        route["origin"] = origin
        route["destination"] = destination
        route["is_estimated"] = False
        return _add_variability(route)
    
    # Try reverse route
    key_reverse = (destination, origin)
    if key_reverse in INDIAN_ROUTES:
        route = INDIAN_ROUTES[key_reverse].copy()
        route["origin"] = origin
        route["destination"] = destination
        route["is_estimated"] = False
        return _add_variability(route)
    
    # Estimate route if not found
    return _estimate_route(origin, destination)


def _add_variability(route: Dict[str, Any]) -> Dict[str, Any]:
    """Add realistic variability to route estimates."""
    # Add 10-30% variability to time estimates
    variability = random.uniform(0.9, 1.3)
    route["estimated_hours"] = round(route["base_hours"] * variability, 1)
    
    # Calculate ETA range
    route["eta_optimistic_hours"] = round(route["base_hours"] * 0.9, 1)
    route["eta_expected_hours"] = round(route["base_hours"] * 1.15, 1)
    route["eta_pessimistic_hours"] = round(route["base_hours"] * 1.5, 1)
    
    return route


def _estimate_route(origin: str, destination: str) -> Dict[str, Any]:
    """
    Estimate route data when not in hardcoded database.
    Uses rough approximations.
    """
    # Rough distance estimate (placeholder)
    # In reality, this would use some distance calculation
    estimated_distance = random.randint(200, 1500)
    
    # Estimate other values based on distance
    base_hours = estimated_distance / 50  # ~50 km/h average for trucks
    
    return {
        "origin": origin,
        "destination": destination,
        "distance_km": estimated_distance,
        "base_hours": round(base_hours, 1),
        "estimated_hours": round(base_hours * random.uniform(1.0, 1.3), 1),
        "highways": ["NH (Estimated)"],
        "tolls": max(1, estimated_distance // 100),
        "toll_cost": estimated_distance * 2,  # ~₹2 per km
        "checkpoints": ["State Border (Estimated)"],
        "fuel_stops": max(1, estimated_distance // 300),
        "risk_level": "unknown",
        "is_estimated": True,
        "eta_optimistic_hours": round(base_hours * 0.9, 1),
        "eta_expected_hours": round(base_hours * 1.15, 1),
        "eta_pessimistic_hours": round(base_hours * 1.5, 1),
    }


def get_all_cities() -> list:
    """Get list of all cities in the route database."""
    cities = set()
    for origin, dest in INDIAN_ROUTES.keys():
        cities.add(origin)
        cities.add(dest)
    return sorted(list(cities))
