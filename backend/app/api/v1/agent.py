"""
Neuro-Logistics Supervisor Agent API Endpoints.

Provides REST API for the AI agent's decision loop and features.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime
import json

from app.services.ai.supervisor import (
    NeuroLogisticsSupervisor,
    get_or_create_supervisor,
    TruckState,
    MissionState,
    EnvironmentState,
    JourneyState,
)

router = APIRouter(prefix="/agent", tags=["AI Agent"])


# ==========================================
# REQUEST/RESPONSE MODELS
# ==========================================

class TruckStateRequest(BaseModel):
    vehicle_id: str
    registration_number: str
    current_location: Dict[str, float]
    current_city: str
    speed_kmh: float = 0
    fuel_level_percent: float = 100
    max_capacity_tons: float = 28
    current_load_tons: float = 0
    driver_name: str
    driver_hours_remaining: float = 11


class MissionStateRequest(BaseModel):
    mission_id: str
    origin: str
    destination: str
    origin_address: str
    destination_address: str
    cargo_type: str
    weight_tons: float
    distance_km: float
    progress_km: float = 0
    base_fare: float
    toll_cost: float = 0
    fuel_cost_estimated: float = 0
    started_at: str
    expected_arrival: str
    checkpoints: List[Dict[str, Any]] = []
    current_checkpoint_index: int = 0


class EnvironmentStateRequest(BaseModel):
    weather_condition: str = "clear"
    traffic_level: str = "light"
    road_condition: str = "good"
    delay_probability: float = 0.1
    current_fuel_price: float = 105.0
    toll_queue_minutes: int = 5
    border_crossing_delay_minutes: int = 15
    is_festival_season: bool = False
    is_strike_alert: bool = False
    connectivity_status: str = "good"


class DecisionLoopRequest(BaseModel):
    truck: TruckStateRequest
    mission: Optional[MissionStateRequest] = None
    environment: EnvironmentStateRequest
    available_loads: List[Dict[str, Any]] = []


class SmartPlanRequest(BaseModel):
    truck_id: str
    registration_number: str
    origin: str
    destination: str
    cargo_type: str
    weight_tons: float


class BackhaulRequest(BaseModel):
    destination: str
    home_base: str
    truck_id: str
    max_capacity_tons: float
    current_load_tons: float = 0
    completion_time: str


class LtlAnalysisRequest(BaseModel):
    truck_id: str
    max_capacity_tons: float
    current_load_tons: float
    current_mission_origin: str
    current_mission_destination: str


class CostCalculationRequest(BaseModel):
    """Request model for cost calculation between two cities."""
    origin: str = Field(..., description="Origin city name")
    destination: str = Field(..., description="Destination city name")
    weight_tons: float = Field(default=10, description="Cargo weight in tons")
    cargo_type: str = Field(default="General", description="Type of cargo")
    vehicle_type: str = Field(default="HCV", description="Vehicle type: HCV, MAV, LCV")
    include_return: bool = Field(default=False, description="Include return journey cost")


# ==========================================
# API ENDPOINTS
# ==========================================

@router.post("/calculate-cost", summary="Calculate cost between two cities")
async def calculate_cost(request: CostCalculationRequest):
    """
    Calculate comprehensive trip cost between two cities using AI agent.
    
    This endpoint calls the Neuro-Logistics Supervisor agent to:
    - Analyze the route
    - Calculate costs
    - Provide AI-powered insights and recommendations
    
    Returns:
    - Route details (distance, duration, highways)
    - Cost breakdown (fuel, tolls, driver, misc)
    - Fare calculation (base fare, effort multiplier, total)
    - ETA range (optimistic, expected, pessimistic)
    - Profit analysis for fleet operators
    - AI-generated insights from Grok agent
    """
    try:
        from app.services.maps import get_maps_service
        from app.services.ai.grok_client import get_grok_client, GrokClient
        from datetime import timedelta
        
        maps = get_maps_service()
        
        # Get route information
        route = maps.get_route(request.origin, request.destination)
        
        # Calculate toll costs
        toll_cost = sum(t.get("cost", 0) for t in route.tolls)
        
        # Fuel consumption calculation
        # HCV: ~3.5 km/L, MAV: ~4 km/L, LCV: ~6 km/L
        fuel_efficiency = {"HCV": 3.5, "MAV": 4.0, "LCV": 6.0}
        kmpl = fuel_efficiency.get(request.vehicle_type.upper(), 4.0)
        fuel_needed_liters = route.distance_km / kmpl
        fuel_price_per_liter = 105.0  # Current diesel price
        fuel_cost = fuel_needed_liters * fuel_price_per_liter
        
        # Driver cost
        driver_cost_per_hour = 150
        driver_cost = route.duration_hours * driver_cost_per_hour
        
        # Misc costs (maintenance, insurance per trip)
        misc_cost = route.distance_km * 2  # ₹2 per km
        
        # Total operating cost
        total_operating_cost = fuel_cost + toll_cost + driver_cost + misc_cost
        
        # Fare calculation with effort multiplier
        base_rate_per_km = 55  # Base rate per km
        base_fare = route.distance_km * base_rate_per_km
        
        # Effort multiplier based on conditions
        effort_multiplier = 1.0
        
        # Weight factor
        if request.weight_tons > 20:
            effort_multiplier += 0.15
        elif request.weight_tons > 15:
            effort_multiplier += 0.10
        elif request.weight_tons > 10:
            effort_multiplier += 0.05
        
        # Border crossings
        border_crossings = len(route.checkpoints) if hasattr(route, 'checkpoints') else 0
        effort_multiplier += border_crossings * 0.02
        
        # Cargo type factor
        cargo_factors = {
            "hazmat": 0.20, "chemicals": 0.15, "perishable": 0.12,
            "fragile": 0.10, "electronics": 0.08, "general": 0.0
        }
        cargo_factor = cargo_factors.get(request.cargo_type.lower(), 0.0)
        effort_multiplier += cargo_factor
        
        # Calculate final fare
        adjusted_fare = base_fare * effort_multiplier
        total_fare = adjusted_fare + toll_cost + (fuel_cost * 0.3)  # Fuel surcharge
        
        # Profit calculation
        gross_profit = total_fare - total_operating_cost
        profit_margin = (gross_profit / total_fare) * 100 if total_fare > 0 else 0
        
        # ETA calculation with ranges
        base_hours = route.duration_hours
        eta_optimistic = base_hours * 0.9
        eta_expected = base_hours * 1.15  # 15% buffer
        eta_pessimistic = base_hours * 1.5  # 50% buffer for delays
        
        now = datetime.now()
        
        # Return journey cost (if requested)
        return_journey = None
        if request.include_return:
            return_journey = {
                "distance_km": route.distance_km,
                "empty_return_cost": {
                    "fuel_cost": round(fuel_cost * 0.85),  # Lighter truck
                    "toll_cost": round(toll_cost * 0.6),  # Empty vehicle discount
                    "driver_cost": round(driver_cost),
                    "total": round(fuel_cost * 0.85 + toll_cost * 0.6 + driver_cost)
                },
                "recommendation": "Book backhaul load to avoid dead miles",
                "potential_backhaul_earnings": round(total_fare * 0.7)
            }
        
        # ==========================================
        # CALL AI AGENT FOR INTELLIGENT INSIGHTS
        # ==========================================
        ai_insights = []
        ai_analysis = None
        agent_used = False
        
        try:
            grok_client = get_grok_client()
            
            # Call the AI agent to analyze the mission
            ai_analysis = await grok_client.analyze_mission(
                origin=request.origin,
                destination=request.destination,
                cargo_type=request.cargo_type,
                weight_tons=request.weight_tons,
                vehicle_type=request.vehicle_type,
            )
            agent_used = True
            
            # Extract insights from AI response
            if isinstance(ai_analysis, dict):
                if "route_advice" in ai_analysis:
                    ai_insights.append(f"🛣️ Route: {ai_analysis['route_advice']}")
                if "risks" in ai_analysis:
                    risks = ai_analysis['risks']
                    if isinstance(risks, list):
                        ai_insights.append(f"⚠️ Risks: {', '.join(risks[:2])}")
                    else:
                        ai_insights.append(f"⚠️ Risks: {risks}")
                if "estimated_delays" in ai_analysis:
                    ai_insights.append(f"⏱️ Expected Delays: {ai_analysis['estimated_delays']}")
                if "fuel_stops" in ai_analysis:
                    ai_insights.append(f"⛽ Fuel Stops: {ai_analysis['fuel_stops']}")
                if "best_departure" in ai_analysis:
                    ai_insights.append(f"🕐 Best Departure: {ai_analysis['best_departure']}")
                if "raw_response" in ai_analysis:
                    # If JSON parsing failed, extract key insights from raw text
                    raw = ai_analysis['raw_response'][:500]
                    ai_insights.append(f"🤖 AI Analysis: {raw}")
            
        except Exception as ai_error:
            # AI agent not available, use fallback insights
            agent_used = False
            ai_insights = []
        
        # Add calculated insights (always present)
        calculated_insights = [
            f"📍 Route: {request.origin} → {request.destination} ({route.distance_km} km)",
            f"🛣️ Via: {', '.join(route.highways[:2]) if route.highways else 'Direct route'}",
            f"💰 Recommended Fare: ₹{round(total_fare):,} (₹{round(total_fare/route.distance_km)}/km)",
            f"📊 Effort Multiplier: {effort_multiplier:.2f}x for {request.cargo_type} cargo",
            f"💵 Profit Margin: {profit_margin:.1f}% (₹{round(gross_profit):,} profit)",
        ]
        
        if request.include_return:
            calculated_insights.append(
                f"🔄 Empty return cost: ₹{return_journey['empty_return_cost']['total']:,} - Book backhaul to save!"
            )
        else:
            calculated_insights.append(
                "💡 Tip: Enable 'Include Return Journey' to analyze dead mile costs"
            )
        
        # Combine AI insights with calculated insights
        final_insights = ai_insights + calculated_insights if ai_insights else calculated_insights
        
        return {
            "success": True,
            "agent_used": agent_used,
            "calculation": {
                "origin": request.origin,
                "destination": request.destination,
                "cargo": {
                    "type": request.cargo_type,
                    "weight_tons": request.weight_tons
                },
                "vehicle_type": request.vehicle_type,
                
                "route": {
                    "distance_km": route.distance_km,
                    "duration_hours": round(route.duration_hours, 1),
                    "highways": route.highways,
                    "toll_plazas": len(route.tolls),
                    "border_crossings": border_crossings,
                    "is_estimated": route.is_estimated
                },
                
                "cost_breakdown": {
                    "fuel": {
                        "liters_needed": round(fuel_needed_liters, 1),
                        "price_per_liter": fuel_price_per_liter,
                        "total": round(fuel_cost)
                    },
                    "tolls": round(toll_cost),
                    "driver": round(driver_cost),
                    "misc": round(misc_cost),
                    "total_operating_cost": round(total_operating_cost)
                },
                
                "fare_calculation": {
                    "base_fare": round(base_fare),
                    "effort_multiplier": round(effort_multiplier, 2),
                    "adjusted_fare": round(adjusted_fare),
                    "fuel_surcharge": round(fuel_cost * 0.3),
                    "toll_pass_through": round(toll_cost),
                    "total_fare": round(total_fare),
                    "rate_per_km": round(total_fare / route.distance_km, 2)
                },
                
                "profit_analysis": {
                    "total_fare": round(total_fare),
                    "total_cost": round(total_operating_cost),
                    "gross_profit": round(gross_profit),
                    "profit_margin_percent": round(profit_margin, 1)
                },
                
                "eta_range": {
                    "optimistic": {
                        "hours": round(eta_optimistic, 1),
                        "arrival": (now + timedelta(hours=eta_optimistic)).strftime("%Y-%m-%d %H:%M")
                    },
                    "expected": {
                        "hours": round(eta_expected, 1),
                        "arrival": (now + timedelta(hours=eta_expected)).strftime("%Y-%m-%d %H:%M")
                    },
                    "pessimistic": {
                        "hours": round(eta_pessimistic, 1),
                        "arrival": (now + timedelta(hours=eta_pessimistic)).strftime("%Y-%m-%d %H:%M")
                    }
                },
                
                "return_journey": return_journey
            },
            
            "ai_insights": final_insights,
            "ai_raw_analysis": ai_analysis if agent_used else None,
        }
        

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cost calculation failed: {str(e)}"
        )

@router.post("/decision-loop", summary="Run agent decision loop")
async def run_decision_loop(request: DecisionLoopRequest):
    """
    Run the main decision loop: Observe → Reason → Decide → Act
    
    This is the core endpoint for the Neuro-Logistics Supervisor.
    Returns the agent's decision based on current state.
    """
    try:
        supervisor = get_or_create_supervisor(request.truck.vehicle_id)
        await supervisor.initialize()
        
        # Convert request to internal state objects
        truck_state = TruckState(
            vehicle_id=request.truck.vehicle_id,
            registration_number=request.truck.registration_number,
            current_location=request.truck.current_location,
            current_city=request.truck.current_city,
            speed_kmh=request.truck.speed_kmh,
            fuel_level_percent=request.truck.fuel_level_percent,
            max_capacity_tons=request.truck.max_capacity_tons,
            current_load_tons=request.truck.current_load_tons,
            driver_name=request.truck.driver_name,
            driver_hours_remaining=request.truck.driver_hours_remaining,
            last_update=datetime.now().isoformat(),
        )
        
        mission_state = None
        if request.mission:
            mission_state = MissionState(
                mission_id=request.mission.mission_id,
                origin=request.mission.origin,
                destination=request.mission.destination,
                origin_address=request.mission.origin_address,
                destination_address=request.mission.destination_address,
                cargo_type=request.mission.cargo_type,
                weight_tons=request.mission.weight_tons,
                distance_km=request.mission.distance_km,
                progress_km=request.mission.progress_km,
                base_fare=request.mission.base_fare,
                toll_cost=request.mission.toll_cost,
                fuel_cost_estimated=request.mission.fuel_cost_estimated,
                started_at=request.mission.started_at,
                expected_arrival=request.mission.expected_arrival,
                checkpoints=request.mission.checkpoints,
                current_checkpoint_index=request.mission.current_checkpoint_index,
            )
        
        environment = EnvironmentState(
            weather_condition=request.environment.weather_condition,
            traffic_level=request.environment.traffic_level,
            road_condition=request.environment.road_condition,
            delay_probability=request.environment.delay_probability,
            current_fuel_price=request.environment.current_fuel_price,
            toll_queue_minutes=request.environment.toll_queue_minutes,
            border_crossing_delay_minutes=request.environment.border_crossing_delay_minutes,
            is_festival_season=request.environment.is_festival_season,
            is_strike_alert=request.environment.is_strike_alert,
            connectivity_status=request.environment.connectivity_status,
        )
        
        # Run decision loop
        decision = await supervisor.run_decision_loop(
            truck_state,
            mission_state,
            environment,
            request.available_loads,
        )
        
        return {
            "success": True,
            "agent_id": request.truck.vehicle_id,
            "timestamp": datetime.now().isoformat(),
            "decision": {
                "type": decision.decision_type.value,
                "action": decision.action_details,
                "priority": decision.priority,
                "expected_benefit": decision.expected_benefit,
            },
            "reasoning": {
                "observations": decision.reasoning.observations,
                "constraints": decision.reasoning.constraints,
                "opportunities": decision.reasoning.opportunities,
                "risks": decision.reasoning.risks,
                "trade_offs": decision.reasoning.trade_offs,
                "recommendation": decision.reasoning.recommendation,
                "confidence": decision.reasoning.confidence,
            },
            "agent_state": supervisor.get_state_summary(),
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Decision loop failed: {str(e)}"
        )


@router.post("/plan-trip", summary="Generate smart trip plan")
async def plan_trip(request: SmartPlanRequest):
    """
    Generate a smart trip plan before the journey.
    
    Features:
    - Realistic route (accounts for borders, restrictions)
    - Dynamic effort-based fare calculation
    - ETA range (not single optimistic time)
    - Pre-identified backhaul opportunities
    """
    try:
        supervisor = get_or_create_supervisor(request.truck_id)
        await supervisor.initialize()
        
        # Create truck state
        truck = TruckState(
            vehicle_id=request.truck_id,
            registration_number=request.registration_number,
            current_location={"lat": 0, "lng": 0},
            current_city=request.origin,
            speed_kmh=0,
            fuel_level_percent=100,
            max_capacity_tons=28,
            current_load_tons=request.weight_tons,
            driver_name="Driver",
            driver_hours_remaining=11,
            last_update=datetime.now().isoformat(),
        )
        
        # Generate smart plan
        plan = await supervisor.generate_smart_plan(
            truck,
            request.origin,
            request.destination,
            request.cargo_type,
            request.weight_tons,
        )
        
        return {
            "success": True,
            "plan": plan,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trip planning failed: {str(e)}"
        )


@router.post("/find-backhaul", summary="Find backhaul opportunities")
async def find_backhaul(request: BackhaulRequest):
    """
    Find backhaul opportunities to avoid dead miles.
    
    Analyzes available return loads and recommends the best option.
    """
    try:
        supervisor = get_or_create_supervisor(request.truck_id)
        
        truck = TruckState(
            vehicle_id=request.truck_id,
            registration_number=request.truck_id,
            current_location={"lat": 0, "lng": 0},
            current_city=request.destination,
            speed_kmh=0,
            fuel_level_percent=50,
            max_capacity_tons=request.max_capacity_tons,
            current_load_tons=request.current_load_tons,
            driver_name="Driver",
            driver_hours_remaining=8,
            last_update=datetime.now().isoformat(),
        )
        
        result = supervisor.find_backhaul_opportunities(
            request.destination,
            request.home_base,
            truck,
            request.completion_time,
        )
        
        return {
            "success": True,
            "backhaul_analysis": result,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Backhaul search failed: {str(e)}"
        )


@router.post("/analyze-ltl", summary="Analyze LTL pooling opportunities")
async def analyze_ltl(request: LtlAnalysisRequest):
    """
    Analyze opportunities to pool LTL (Less Than Load) shipments.
    
    Finds small en-route loads that can fill unused capacity.
    """
    try:
        supervisor = get_or_create_supervisor(request.truck_id)
        
        truck = TruckState(
            vehicle_id=request.truck_id,
            registration_number=request.truck_id,
            current_location={"lat": 0, "lng": 0},
            current_city=request.current_mission_origin,
            speed_kmh=0,
            fuel_level_percent=80,
            max_capacity_tons=request.max_capacity_tons,
            current_load_tons=request.current_load_tons,
            driver_name="Driver",
            driver_hours_remaining=10,
            last_update=datetime.now().isoformat(),
        )
        
        mission = MissionState(
            mission_id="current",
            origin=request.current_mission_origin,
            destination=request.current_mission_destination,
            origin_address=request.current_mission_origin,
            destination_address=request.current_mission_destination,
            cargo_type="General",
            weight_tons=request.current_load_tons,
            distance_km=500,
            progress_km=0,
            base_fare=30000,
            toll_cost=2000,
            fuel_cost_estimated=8000,
            started_at=datetime.now().isoformat(),
            expected_arrival=datetime.now().isoformat(),
            checkpoints=[],
            current_checkpoint_index=0,
        )
        
        # Mock nearby loads
        nearby_loads = [
            {
                "id": "ltl-001",
                "shipper": "ABC Corp",
                "cargo_type": "Electronics",
                "weight_tons": 3,
                "pickup_city": request.current_mission_origin,
                "delivery_city": request.current_mission_destination,
                "offered_rate": 12000,
                "detour_km": 8,
            },
            {
                "id": "ltl-002",
                "shipper": "XYZ Ltd",
                "cargo_type": "Textiles",
                "weight_tons": 4,
                "pickup_city": request.current_mission_origin,
                "delivery_city": request.current_mission_destination,
                "offered_rate": 15000,
                "detour_km": 12,
            },
            {
                "id": "ltl-003",
                "shipper": "Quick Ship",
                "cargo_type": "Parcels",
                "weight_tons": 2,
                "pickup_city": request.current_mission_origin,
                "delivery_city": request.current_mission_destination,
                "offered_rate": 8000,
                "detour_km": 5,
            },
        ]
        
        result = supervisor.analyze_capacity_opportunity(
            truck,
            mission,
            nearby_loads,
        )
        
        return {
            "success": True,
            "ltl_analysis": result,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LTL analysis failed: {str(e)}"
        )


@router.get("/{truck_id}/state", summary="Get agent state")
def get_agent_state(truck_id: str):
    """
    Get current state of the AI agent for a specific truck.
    """
    try:
        supervisor = get_or_create_supervisor(truck_id)
        return {
            "success": True,
            "state": supervisor.get_state_summary(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent state: {str(e)}"
        )


# ==========================================
# DEMO SCENARIO ENDPOINTS
# ==========================================

@router.get("/demo/decision-example", summary="Demo: Decision loop example")
def demo_decision_example():
    """
    Returns a complete example of the decision loop output.
    
    Use this to understand how the agent makes decisions.
    """
    return {
        "scenario": "Traffic detected, rerouting decision",
        "timestamp": datetime.now().isoformat(),
        
        "observe": {
            "journey_state": "in_transit",
            "truck": {
                "id": "v-001",
                "registration": "MH12AB1234",
                "location": {"lat": 22.31, "lng": 73.18},
                "city": "Near Vadodara",
                "fuel_percent": 45,
                "load_tons": 12.5,
                "driver_hours_left": 6.5
            },
            "mission": {
                "origin": "Jaipur",
                "destination": "Mumbai",
                "progress": "60%",
                "remaining_km": 460
            },
            "environment": {
                "traffic": "heavy",
                "weather": "clear",
                "delay_ahead": "2 hours 15 min"
            },
            "alerts": [
                "🚗 Heavy traffic ahead - accident on NH44"
            ]
        },
        
        "reason": {
            "observations": [
                "Traffic jam will cause 2+ hour delay",
                "Driver has 6.5 hours left before rest",
                "Fuel at 45% - sufficient for detour"
            ],
            "constraints": [
                "Must reach Mumbai by 20:00 for delivery window"
            ],
            "opportunities": [
                "Alternative route via Bharuch saves 1.5 hours"
            ],
            "risks": [
                "Staying on current route risks missing delivery"
            ],
            "trade_offs": [
                {
                    "option": "Wait in traffic",
                    "time_cost": "2h 15min",
                    "money_cost": "₹3,200 lost time"
                },
                {
                    "option": "Reroute via Bharuch",
                    "time_cost": "45 min",
                    "money_cost": "₹1,600 extra fuel",
                    "net_benefit": "+₹1,600"
                }
            ],
            "recommendation": "Reroute via Bharuch to save time",
            "confidence": 0.92
        },
        
        "decide": {
            "type": "route_change",
            "action": {
                "command": "Reroute via Bharuch bypass",
                "new_waypoint": "Bharuch",
                "estimated_time_saved": "1h 30min"
            },
            "priority": "high",
            "expected_benefit": {
                "time_saved_hours": 1.5,
                "cost_saved": 1600,
                "delivery_reliability": "improved"
            }
        },
        
        "act": {
            "action_id": "ACT-20260201143000",
            "status": "executing",
            "driver_notification": "🔄 Route changed: Take exit 12B towards Bharuch. New ETA: 19:15",
            "eta_updated": True,
            "new_eta": "2026-02-01T19:15:00+05:30"
        }
    }


@router.get("/demo/agent-capabilities", summary="Demo: Agent capabilities overview")
def demo_agent_capabilities():
    """
    Returns an overview of all agent capabilities for the demo.
    """
    return {
        "agent_name": "Neuro-Logistics Supervisor",
        "tagline": "One AI Agent. Three Pillars. Zero Dead Miles.",
        
        "decision_loop": {
            "description": "Continuously cycles through: Observe → Reason → Decide → Act",
            "frequency": "Every 30 seconds during active mission",
            "adaptability": "Dynamically switches behavior based on journey state"
        },
        
        "modules": {
            "smart_planning": {
                "phase": "Before Trip",
                "capabilities": [
                    "Generates truck-friendly routes (avoids low bridges, narrow roads)",
                    "Calculates dynamic effort-based fare",
                    "Produces ETA range (optimistic/expected/pessimistic)",
                    "Pre-identifies return load options"
                ],
                "problems_solved": [
                    "Static plan trap",
                    "Unrealistic single-point ETAs",
                    "Fixed per-km pricing that ignores effort"
                ]
            },
            "live_adaptation": {
                "phase": "During Trip",
                "capabilities": [
                    "Real-time traffic monitoring",
                    "Smart rerouting when profitable",
                    "Fuel and rest stop optimization",
                    "Dynamic ETA updates"
                ],
                "problems_solved": [
                    "Route rigidity",
                    "Variable time estimates",
                    "Missed delivery windows"
                ]
            },
            "capacity_optimization": {
                "phase": "Throughout Journey",
                "capabilities": [
                    "Tracks unused truck space in real-time",
                    "Finds en-route LTL loads to fill capacity",
                    "Pre-books return loads before reaching destination",
                    "Calculates profitability of each opportunity"
                ],
                "problems_solved": [
                    "Dead mile crisis",
                    "Underutilized capacity",
                    "Empty return journeys"
                ]
            }
        },
        
        "indian_context": {
            "challenges_addressed": [
                "State border complexities and delays",
                "Realistic traffic patterns on highways",
                "Poor connectivity in remote areas",
                "Festival season demand spikes",
                "Strike and bandh alerts"
            ],
            "solutions": [
                "Delay probabilities instead of ideal times",
                "Hybrid online/offline operation",
                "Cached route data for poor connectivity",
                "Festival-aware pricing and routing",
                "Safety-first decision making"
            ]
        },
        
        "measurable_outcomes": {
            "dead_mile_reduction": "Up to 40%",
            "capacity_utilization_improvement": "30-50%",
            "earnings_increase": "25-35%",
            "fuel_cost_optimization": "8-12%",
            "on_time_delivery_improvement": "15-20%"
        }
    }
