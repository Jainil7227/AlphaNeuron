"""
Demo Data API Endpoints.

Provides pre-populated demo data for testing the AI agent
without requiring a database connection.
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, timedelta
import random

router = APIRouter(prefix="/demo", tags=["Demo Data"])


# ==========================================
# DEMO DATA: VEHICLES
# ==========================================

DEMO_VEHICLES = [
    {
        "id": "v-001",
        "registration_number": "MH12AB1234",
        "vehicle_type": "HCV",
        "make": "Tata",
        "model": "Prima 4928.S",
        "year": 2022,
        "max_capacity_tons": 28,
        "current_load_tons": 12.5,
        "status": "on_mission",
        "driver_name": "Rajesh Kumar",
        "driver_phone": "+919876543210",
        "current_location": {"lat": 19.0760, "lng": 72.8777},
        "last_update": "2026-02-01T05:30:00",
        "fuel_level_percent": 65,
    },
    {
        "id": "v-002",
        "registration_number": "GJ05CD5678",
        "vehicle_type": "HCV",
        "make": "Ashok Leyland",
        "model": "Captain 2523",
        "year": 2021,
        "max_capacity_tons": 25,
        "current_load_tons": 0,
        "status": "available",
        "driver_name": "Suresh Patel",
        "driver_phone": "+919876543211",
        "current_location": {"lat": 23.0225, "lng": 72.5714},
        "last_update": "2026-02-01T05:45:00",
        "fuel_level_percent": 85,
    },
    {
        "id": "v-003",
        "registration_number": "RJ14EF9012",
        "vehicle_type": "MAV",
        "make": "BharatBenz",
        "model": "4928T",
        "year": 2023,
        "max_capacity_tons": 35,
        "current_load_tons": 28,
        "status": "on_mission",
        "driver_name": "Anil Sharma",
        "driver_phone": "+919876543212",
        "current_location": {"lat": 26.9124, "lng": 75.7873},
        "last_update": "2026-02-01T05:40:00",
        "fuel_level_percent": 45,
    },
    {
        "id": "v-004",
        "registration_number": "DL01GH3456",
        "vehicle_type": "LCV",
        "make": "Mahindra",
        "model": "Blazo X 35",
        "year": 2022,
        "max_capacity_tons": 16,
        "current_load_tons": 8,
        "status": "on_mission",
        "driver_name": "Vikram Singh",
        "driver_phone": "+919876543213",
        "current_location": {"lat": 28.6139, "lng": 77.2090},
        "last_update": "2026-02-01T05:35:00",
        "fuel_level_percent": 55,
    },
    {
        "id": "v-005",
        "registration_number": "KA01IJ7890",
        "vehicle_type": "HCV",
        "make": "Eicher",
        "model": "Pro 6049",
        "year": 2021,
        "max_capacity_tons": 26,
        "current_load_tons": 0,
        "status": "maintenance",
        "driver_name": "Ravi Reddy",
        "driver_phone": "+919876543214",
        "current_location": {"lat": 12.9716, "lng": 77.5946},
        "last_update": "2026-02-01T04:00:00",
        "fuel_level_percent": 30,
    },
]


# ==========================================
# DEMO DATA: ACTIVE MISSIONS
# ==========================================

DEMO_MISSIONS = [
    {
        "id": "m-001",
        "vehicle_id": "v-001",
        "vehicle_number": "MH12AB1234",
        "driver_name": "Rajesh Kumar",
        "status": "in_transit",
        "origin": "Mumbai",
        "destination": "Delhi",
        "origin_address": "JNPT Port, Navi Mumbai",
        "destination_address": "Narela Industrial Area, Delhi",
        "cargo_type": "Industrial Machinery",
        "weight_tons": 12.5,
        "distance_km": 1420,
        "estimated_duration_hours": 24,
        "progress_percent": 35,
        "current_location": {"lat": 21.1458, "lng": 79.0882},  # Near Nagpur
        "started_at": "2026-01-31T18:00:00",
        "expected_arrival": "2026-02-01T18:00:00",
        "fare_amount": 85000,
        "toll_cost": 4500,
        "fuel_cost_estimated": 18000,
        "checkpoints_passed": 2,
        "total_checkpoints": 6,
        "alerts": [],
    },
    {
        "id": "m-002",
        "vehicle_id": "v-003",
        "vehicle_number": "RJ14EF9012",
        "driver_name": "Anil Sharma",
        "status": "in_transit",
        "origin": "Jaipur",
        "destination": "Mumbai",
        "origin_address": "Sitapura Industrial Area, Jaipur",
        "destination_address": "Bhiwandi Warehouse, Mumbai",
        "cargo_type": "Textiles",
        "weight_tons": 28,
        "distance_km": 1150,
        "estimated_duration_hours": 20,
        "progress_percent": 60,
        "current_location": {"lat": 22.3072, "lng": 73.1812},  # Near Vadodara
        "started_at": "2026-01-31T12:00:00",
        "expected_arrival": "2026-02-01T08:00:00",
        "fare_amount": 95000,
        "toll_cost": 3800,
        "fuel_cost_estimated": 15000,
        "checkpoints_passed": 4,
        "total_checkpoints": 5,
        "alerts": ["⚠️ Traffic delay expected near Ahmedabad"],
    },
    {
        "id": "m-003",
        "vehicle_id": "v-004",
        "vehicle_number": "DL01GH3456",
        "driver_name": "Vikram Singh",
        "status": "loading",
        "origin": "Delhi",
        "destination": "Kolkata",
        "origin_address": "Okhla Industrial Area, Delhi",
        "destination_address": "Salt Lake City, Kolkata",
        "cargo_type": "Electronics",
        "weight_tons": 8,
        "distance_km": 1530,
        "estimated_duration_hours": 26,
        "progress_percent": 5,
        "current_location": {"lat": 28.5535, "lng": 77.2588},  # Okhla, Delhi
        "started_at": "2026-02-01T04:00:00",
        "expected_arrival": "2026-02-02T06:00:00",
        "fare_amount": 72000,
        "toll_cost": 4200,
        "fuel_cost_estimated": 20000,
        "checkpoints_passed": 0,
        "total_checkpoints": 7,
        "alerts": [],
    },
]


# ==========================================
# DEMO DATA: AVAILABLE LOADS (Backhaul Opportunities)
# ==========================================

DEMO_LOADS = [
    {
        "id": "l-001",
        "shipper_name": "Steel Authority of India",
        "cargo_type": "Steel Coils",
        "weight_tons": 22,
        "pickup_city": "Nagpur",
        "pickup_address": "MIDC Hingna, Nagpur",
        "delivery_city": "Mumbai",
        "delivery_address": "Taloja Industrial Area",
        "distance_km": 820,
        "offered_rate": 55000,
        "rate_per_km": 67,
        "pickup_window": "2026-02-01T10:00-14:00",
        "delivery_deadline": "2026-02-02T18:00:00",
        "special_requirements": ["Heavy Load Equipment", "Covered Trailer"],
        "match_score": 92,
        "backhaul_potential": True,
        "detour_km": 15,
    },
    {
        "id": "l-002",
        "shipper_name": "Asian Paints Ltd",
        "cargo_type": "Paint Drums",
        "weight_tons": 15,
        "pickup_city": "Vadodara",
        "pickup_address": "GIDC Makarpura, Vadodara",
        "delivery_city": "Pune",
        "delivery_address": "Chakan Industrial Zone",
        "distance_km": 420,
        "offered_rate": 32000,
        "rate_per_km": 76,
        "pickup_window": "2026-02-01T08:00-12:00",
        "delivery_deadline": "2026-02-01T22:00:00",
        "special_requirements": ["Hazmat Certified", "Temperature Controlled"],
        "match_score": 85,
        "backhaul_potential": True,
        "detour_km": 25,
    },
    {
        "id": "l-003",
        "shipper_name": "Reliance Retail",
        "cargo_type": "FMCG Products",
        "weight_tons": 18,
        "pickup_city": "Ahmedabad",
        "pickup_address": "Sanand Industrial Park",
        "delivery_city": "Jaipur",
        "delivery_address": "VKI Area, Jaipur",
        "distance_km": 670,
        "offered_rate": 48000,
        "rate_per_km": 72,
        "pickup_window": "2026-02-01T06:00-10:00",
        "delivery_deadline": "2026-02-01T20:00:00",
        "special_requirements": ["Food Grade Trailer"],
        "match_score": 78,
        "backhaul_potential": True,
        "detour_km": 45,
    },
    {
        "id": "l-004",
        "shipper_name": "Maruti Suzuki",
        "cargo_type": "Auto Parts",
        "weight_tons": 12,
        "pickup_city": "Gurgaon",
        "pickup_address": "Manesar Industrial Area",
        "delivery_city": "Chennai",
        "delivery_address": "Oragadam Industrial Corridor",
        "distance_km": 2180,
        "offered_rate": 145000,
        "rate_per_km": 66,
        "pickup_window": "2026-02-01T14:00-18:00",
        "delivery_deadline": "2026-02-04T10:00:00",
        "special_requirements": ["JIT Delivery", "GPS Tracking Required"],
        "match_score": 88,
        "backhaul_potential": False,
        "detour_km": 0,
    },
]


# ==========================================
# DEMO DATA: AI AGENT INSIGHTS
# ==========================================

DEMO_AI_INSIGHTS = [
    {
        "id": "insight-001",
        "type": "backhaul_opportunity",
        "priority": "high",
        "title": "Backhaul Opportunity Detected",
        "message": "Vehicle MH12AB1234 completing Mumbai-Delhi run can pick up Steel Coils from Nagpur to Mumbai. Potential earning: ₹55,000",
        "action_required": True,
        "potential_savings": 55000,
        "vehicle_id": "v-001",
        "load_id": "l-001",
        "created_at": "2026-02-01T05:30:00",
    },
    {
        "id": "insight-002",
        "type": "route_optimization",
        "priority": "medium",
        "title": "Route Deviation Suggested",
        "message": "Traffic congestion detected on NH44 near Vadodara. Alternative route via Bharuch saves 45 minutes.",
        "action_required": False,
        "potential_savings": 2500,
        "vehicle_id": "v-003",
        "created_at": "2026-02-01T05:25:00",
    },
    {
        "id": "insight-003",
        "type": "ltl_pooling",
        "priority": "high",
        "title": "LTL Pooling Match Found",
        "message": "3 small loads (total 8 tons) can be pooled for Delhi-Jaipur route. Combined fare: ₹42,000 vs individual ₹28,000",
        "action_required": True,
        "potential_savings": 14000,
        "created_at": "2026-02-01T05:20:00",
    },
    {
        "id": "insight-004",
        "type": "fuel_alert",
        "priority": "low",
        "title": "Fuel Stop Recommendation",
        "message": "Vehicle RJ14EF9012 should refuel at HP Vadodara (15km ahead). Current rates ₹2/L cheaper than next station.",
        "action_required": False,
        "potential_savings": 500,
        "vehicle_id": "v-003",
        "created_at": "2026-02-01T05:15:00",
    },
    {
        "id": "insight-005",
        "type": "demand_forecast",
        "priority": "medium",
        "title": "High Demand Zone Alert",
        "message": "Expected 40% increase in freight demand from Ahmedabad next week due to textile exports season.",
        "action_required": False,
        "potential_savings": 0,
        "created_at": "2026-02-01T05:00:00",
    },
]


# ==========================================
# DEMO DATA: FLEET STATISTICS
# ==========================================

DEMO_FLEET_STATS = {
    "total_vehicles": 5,
    "available_vehicles": 1,
    "on_mission_vehicles": 3,
    "maintenance_vehicles": 1,
    "total_capacity_tons": 130,
    "utilized_capacity_tons": 48.5,
    "utilization_percent": 37.3,
    "active_missions": 3,
    "completed_today": 2,
    "revenue_today": 175000,
    "revenue_week": 1250000,
    "revenue_month": 4800000,
    "avg_trip_duration_hours": 18.5,
    "total_distance_today_km": 2450,
    "fuel_consumed_today_liters": 520,
    "co2_saved_kg": 85,
}


# ==========================================
# API ENDPOINTS
# ==========================================

@router.get("/vehicles", summary="Get demo vehicles")
def get_demo_vehicles():
    """Get list of demo vehicles with current status."""
    return {
        "success": True,
        "data": DEMO_VEHICLES,
        "total": len(DEMO_VEHICLES),
    }


@router.get("/missions", summary="Get demo missions")
def get_demo_missions():
    """Get list of active demo missions."""
    return {
        "success": True,
        "data": DEMO_MISSIONS,
        "total": len(DEMO_MISSIONS),
    }


@router.get("/loads", summary="Get available demo loads")
def get_demo_loads():
    """Get list of available loads for matching."""
    return {
        "success": True,
        "data": DEMO_LOADS,
        "total": len(DEMO_LOADS),
    }


@router.get("/insights", summary="Get AI agent insights")
def get_demo_insights():
    """Get AI-generated insights and recommendations."""
    return {
        "success": True,
        "data": DEMO_AI_INSIGHTS,
        "total": len(DEMO_AI_INSIGHTS),
        "action_required_count": sum(1 for i in DEMO_AI_INSIGHTS if i.get("action_required")),
    }


@router.get("/fleet-stats", summary="Get fleet statistics")
def get_demo_fleet_stats():
    """Get fleet-wide statistics for dashboard."""
    return {
        "success": True,
        "data": DEMO_FLEET_STATS,
    }


@router.get("/dashboard", summary="Get complete dashboard data")
def get_demo_dashboard():
    """Get all dashboard data in one call."""
    return {
        "success": True,
        "fleet_stats": DEMO_FLEET_STATS,
        "vehicles": DEMO_VEHICLES,
        "active_missions": DEMO_MISSIONS,
        "available_loads": DEMO_LOADS,
        "ai_insights": DEMO_AI_INSIGHTS,
        "last_updated": datetime.utcnow().isoformat(),
    }


@router.get("/scenario/backhaul", summary="Demo: Backhaul scenario")
def get_backhaul_scenario():
    """
    Get a complete backhaul opportunity scenario for demo.
    
    Shows how AI agent detects and suggests backhaul opportunity.
    """
    vehicle = DEMO_VEHICLES[0]  # MH12AB1234
    mission = DEMO_MISSIONS[0]  # Mumbai-Delhi
    load = DEMO_LOADS[0]  # Steel Coils Nagpur-Mumbai
    
    return {
        "scenario": "Backhaul Opportunity Detection",
        "description": "AI agent detects that vehicle completing Mumbai-Delhi run can pick up return load from Nagpur",
        "vehicle": vehicle,
        "current_mission": mission,
        "opportunity": {
            "load": load,
            "analysis": {
                "detour_required_km": 15,
                "additional_time_hours": 0.5,
                "potential_earning": 55000,
                "fuel_cost_for_detour": 800,
                "net_profit": 54200,
                "recommendation": "ACCEPT",
                "confidence_score": 0.92,
            },
            "ai_reasoning": [
                "Vehicle will be empty after Delhi delivery",
                "Nagpur is only 15km detour from current route",
                "Steel coils match vehicle's capacity (22T < 28T max)",
                "Pickup window aligns with expected arrival time",
                "Rate per km (₹67) is above market average (₹62)",
            ],
        },
    }


@router.get("/scenario/ltl-pooling", summary="Demo: LTL pooling scenario")
def get_ltl_pooling_scenario():
    """
    Get a complete LTL pooling scenario for demo.
    
    Shows how AI agent matches multiple small loads.
    """
    return {
        "scenario": "LTL Pooling Optimization",
        "description": "AI agent pools 3 small loads into one efficient trip",
        "vehicle": DEMO_VEHICLES[1],  # Available HCV
        "loads_to_pool": [
            {
                "id": "ltl-001",
                "shipper": "ABC Electronics",
                "weight_tons": 3,
                "pickup": "Ahmedabad",
                "delivery": "Jaipur",
                "individual_rate": 12000,
            },
            {
                "id": "ltl-002",
                "shipper": "XYZ Pharma",
                "weight_tons": 2.5,
                "pickup": "Ahmedabad",
                "delivery": "Jaipur",
                "individual_rate": 9000,
            },
            {
                "id": "ltl-003",
                "shipper": "Quick Commerce",
                "weight_tons": 2.5,
                "pickup": "Ahmedabad",
                "delivery": "Jaipur",
                "individual_rate": 7000,
            },
        ],
        "optimization": {
            "total_weight": 8,
            "vehicle_capacity": 25,
            "utilization_after_pooling": 32,
            "individual_trips_cost": 28000,
            "pooled_trip_cost": 18000,
            "combined_fare_charged": 42000,
            "customer_savings": 14000,
            "operator_profit": 24000,
            "co2_reduction_kg": 45,
        },
        "ai_reasoning": [
            "3 loads share same origin-destination corridor",
            "Combined weight (8T) fits in single vehicle",
            "Pickup windows overlap (6AM-10AM)",
            "Delivery deadlines compatible",
            "50% cost reduction for shippers",
        ],
    }


@router.get("/scenario/route-optimization", summary="Demo: Route optimization scenario")
def get_route_optimization_scenario():
    """
    Get a complete route optimization scenario for demo.
    
    Shows how AI agent optimizes route based on real-time conditions.
    """
    return {
        "scenario": "Dynamic Route Optimization",
        "description": "AI agent reroutes vehicle to avoid traffic and save time",
        "vehicle": DEMO_VEHICLES[2],  # RJ14EF9012
        "current_mission": DEMO_MISSIONS[1],  # Jaipur-Mumbai
        "original_route": {
            "path": ["Jaipur", "Ajmer", "Udaipur", "Ahmedabad", "Vadodara", "Surat", "Mumbai"],
            "distance_km": 1150,
            "duration_hours": 20,
            "toll_cost": 3800,
            "fuel_cost": 15000,
        },
        "optimized_route": {
            "path": ["Jaipur", "Ajmer", "Ahmedabad", "Bharuch", "Surat", "Mumbai"],
            "distance_km": 1120,
            "duration_hours": 18.5,
            "toll_cost": 3500,
            "fuel_cost": 14200,
            "bypass_reason": "Udaipur route has 2-hour traffic delay",
        },
        "savings": {
            "time_saved_hours": 1.5,
            "distance_saved_km": 30,
            "toll_saved": 300,
            "fuel_saved": 800,
            "total_savings": 1100,
        },
        "ai_reasoning": [
            "Real-time traffic data shows congestion on NH48 near Udaipur",
            "Religious festival causing 2+ hour delays",
            "Alternative via Bharuch adds only 20km but saves 1.5 hours",
            "Toll plazas on alternative route have shorter queues",
            "Weather conditions favorable on both routes",
        ],
    }
