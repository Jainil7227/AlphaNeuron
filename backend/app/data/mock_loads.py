"""
Mock Loads Data

Sample available loads for LTL pooling and backhaul matching.
"""

from typing import List, Dict, Any
import random
from datetime import datetime, timedelta


# Available loads in the market
AVAILABLE_LOADS = [
    # LTL Loads (Small, suitable for pooling)
    {
        "id": "ltl-001",
        "type": "ltl",
        "shipper": "ABC Electronics",
        "cargo_type": "Electronics",
        "weight_tons": 2.5,
        "pickup_city": "Mumbai",
        "delivery_city": "Pune",
        "offered_rate": 8000,
        "pickup_window": "Flexible (2-4 hours)",
        "urgency": "normal",
    },
    {
        "id": "ltl-002",
        "type": "ltl",
        "shipper": "XYZ Textiles",
        "cargo_type": "Textiles",
        "weight_tons": 3.0,
        "pickup_city": "Delhi",
        "delivery_city": "Jaipur",
        "offered_rate": 6500,
        "pickup_window": "Morning only",
        "urgency": "normal",
    },
    {
        "id": "ltl-003",
        "type": "ltl",
        "shipper": "Fresh Foods Co",
        "cargo_type": "Perishables",
        "weight_tons": 1.5,
        "pickup_city": "Bangalore",
        "delivery_city": "Chennai",
        "offered_rate": 12000,
        "pickup_window": "Immediate",
        "urgency": "high",
    },
    {
        "id": "ltl-004",
        "type": "ltl",
        "shipper": "Auto Parts Ltd",
        "cargo_type": "Auto Parts",
        "weight_tons": 4.0,
        "pickup_city": "Chennai",
        "delivery_city": "Hyderabad",
        "offered_rate": 15000,
        "pickup_window": "Today",
        "urgency": "normal",
    },
    {
        "id": "ltl-005",
        "type": "ltl",
        "shipper": "Pharma Express",
        "cargo_type": "Pharmaceuticals",
        "weight_tons": 0.8,
        "pickup_city": "Ahmedabad",
        "delivery_city": "Mumbai",
        "offered_rate": 9000,
        "pickup_window": "ASAP",
        "urgency": "high",
    },
    
    # Full Truckload Backhaul Options
    {
        "id": "ftl-001",
        "type": "backhaul",
        "shipper": "Steel Authority",
        "cargo_type": "Steel Coils",
        "weight_tons": 22,
        "pickup_city": "Mumbai",
        "delivery_city": "Delhi",
        "offered_rate": 65000,
        "pickup_window": "4-6 hours after arrival",
        "urgency": "normal",
    },
    {
        "id": "ftl-002",
        "type": "backhaul",
        "shipper": "Reliance Industries",
        "cargo_type": "Polymer Granules",
        "weight_tons": 18,
        "pickup_city": "Mumbai",
        "delivery_city": "Ahmedabad",
        "offered_rate": 28000,
        "pickup_window": "Next morning",
        "urgency": "normal",
    },
    {
        "id": "ftl-003",
        "type": "backhaul",
        "shipper": "Tata Motors",
        "cargo_type": "Auto Parts",
        "weight_tons": 20,
        "pickup_city": "Pune",
        "delivery_city": "Chennai",
        "offered_rate": 55000,
        "pickup_window": "Flexible",
        "urgency": "normal",
    },
    {
        "id": "ftl-004",
        "type": "backhaul",
        "shipper": "Infosys Logistics",
        "cargo_type": "IT Equipment",
        "weight_tons": 8,
        "pickup_city": "Bangalore",
        "delivery_city": "Hyderabad",
        "offered_rate": 25000,
        "pickup_window": "Today",
        "urgency": "high",
    },
    {
        "id": "ftl-005",
        "type": "backhaul",
        "shipper": "Cotton Corp",
        "cargo_type": "Cotton Bales",
        "weight_tons": 24,
        "pickup_city": "Ahmedabad",
        "delivery_city": "Mumbai",
        "offered_rate": 22000,
        "pickup_window": "2-3 hours",
        "urgency": "normal",
    },
    {
        "id": "ftl-006",
        "type": "backhaul",
        "shipper": "Cement Corp",
        "cargo_type": "Cement",
        "weight_tons": 25,
        "pickup_city": "Hyderabad",
        "delivery_city": "Chennai",
        "offered_rate": 32000,
        "pickup_window": "Immediate",
        "urgency": "normal",
    },
    {
        "id": "ftl-007",
        "type": "backhaul",
        "shipper": "Grain Traders",
        "cargo_type": "Rice",
        "weight_tons": 20,
        "pickup_city": "Kolkata",
        "delivery_city": "Delhi",
        "offered_rate": 75000,
        "pickup_window": "Next day",
        "urgency": "low",
    },
]


def get_available_loads(
    route_origin: str = None,
    route_destination: str = None,
    max_weight: float = None,
    load_type: str = None,
) -> List[Dict[str, Any]]:
    """
    Get available loads, optionally filtered.
    
    Args:
        route_origin: Filter by pickup city along route
        route_destination: Filter by delivery city along route  
        max_weight: Filter by maximum weight capacity
        load_type: Filter by "ltl" or "backhaul"
    """
    loads = AVAILABLE_LOADS.copy()
    
    if load_type:
        loads = [l for l in loads if l["type"] == load_type]
    
    if max_weight:
        loads = [l for l in loads if l["weight_tons"] <= max_weight]
    
    if route_origin:
        route_origin = route_origin.strip().title()
        loads = [l for l in loads if l["pickup_city"] == route_origin]
    
    if route_destination:
        route_destination = route_destination.strip().title()
        loads = [l for l in loads if l["delivery_city"] == route_destination]
    
    # Add dynamic pricing variation
    for load in loads:
        # Simulate market price fluctuation (±15%)
        variation = random.uniform(0.85, 1.15)
        load["current_rate"] = int(load["offered_rate"] * variation)
        load["rate_trend"] = "up" if variation > 1 else "down" if variation < 1 else "stable"
    
    return loads


def get_backhaul_loads(destination: str, home_base: str) -> List[Dict[str, Any]]:
    """
    Get backhaul load options for return journey.
    
    Args:
        destination: Current delivery destination (pickup for backhaul)
        home_base: Driver's home base (delivery for backhaul)
    """
    destination = destination.strip().title()
    home_base = home_base.strip().title()
    
    # Get loads that go from destination towards home
    backhaul_options = []
    
    for load in AVAILABLE_LOADS:
        if load["type"] != "backhaul":
            continue
            
        # Direct match: pickup at destination, delivery at home
        if load["pickup_city"] == destination and load["delivery_city"] == home_base:
            load_copy = load.copy()
            load_copy["match_type"] = "direct"
            load_copy["match_score"] = 95
            backhaul_options.append(load_copy)
            
        # Partial match: pickup at destination, delivery towards home
        elif load["pickup_city"] == destination:
            load_copy = load.copy()
            load_copy["match_type"] = "partial"
            load_copy["match_score"] = 70
            backhaul_options.append(load_copy)
    
    # Sort by match score
    backhaul_options.sort(key=lambda x: x["match_score"], reverse=True)
    
    return backhaul_options


def get_ltl_loads_on_route(
    origin: str,
    destination: str,
    available_capacity: float,
) -> List[Dict[str, Any]]:
    """
    Get LTL loads that can be pooled on the current route.
    
    Finds loads where pickup and delivery are along the route.
    """
    origin = origin.strip().title()
    destination = destination.strip().title()
    
    # Get LTL loads that fit the capacity
    ltl_loads = get_available_loads(load_type="ltl", max_weight=available_capacity)
    
    # In a real system, we'd check if loads are geographically on the route
    # For now, return loads that have matching cities
    route_matches = []
    
    for load in ltl_loads:
        # Check if load is on the same corridor
        if load["pickup_city"] in [origin, destination] or load["delivery_city"] in [origin, destination]:
            load_copy = load.copy()
            load_copy["detour_km"] = random.randint(5, 30)
            load_copy["extra_time_hours"] = round(load_copy["detour_km"] / 40, 1)
            route_matches.append(load_copy)
    
    return route_matches
