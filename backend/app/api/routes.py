"""
Neuro-Logistics API Routes

All API endpoints organized by module:
- Module 1: Mission Planner
- Module 2: Decision Engine
- Module 3: Capacity Manager
- Utility endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import Optional

from app.api.schemas import (
    # Mission Planner
    PlanMissionRequest,
    StartMissionRequest,
    # Decision Engine
    EvaluateSituationRequest,
    EvaluateOpportunityRequest,
    RerouteRequest,
    CopilotChatRequest,
    # Capacity Manager
    FindLTLRequest,
    FindBackhaulRequest,
    AcceptLoadRequest,
    BookBackhaulRequest,
    # Common
    HealthResponse,
    SuccessResponse,
)
from app.modules.mission_planner import MissionPlanner
from app.modules.decision_engine import DecisionEngine
from app.modules.capacity_manager import CapacityManager
from app.data.mock_routes import get_all_cities, get_route_info, INDIAN_ROUTES
from app.data.mock_loads import get_available_loads
from app.data.store import get_store
from app.core import get_gemini_client

router = APIRouter()


# ==========================================
# HEALTH CHECK
# ==========================================

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "modules": {
            "mission_planner": "active",
            "decision_engine": "active",
            "capacity_manager": "active",
        },
    }


# ==========================================
# MODULE 1: MISSION PLANNER
# ==========================================

@router.post("/mission/plan", tags=["Mission Planner"])
async def plan_mission(request: PlanMissionRequest):
    """
    Generate a smart trip plan with dynamic fare and risk assessment.
    
    **Module 1: Context-Aware Mission Planner**
    
    - Calculates realistic ETA with optimistic/expected/pessimistic ranges
    - Generates dynamic fare based on effort (not just distance)
    - Assesses risk factors for the route
    - Pre-identifies return load opportunities
    """
    planner = MissionPlanner()
    
    plan = await planner.plan_mission(
        origin=request.origin,
        destination=request.destination,
        cargo_type=request.cargo_type,
        weight_tons=request.weight_tons,
        vehicle_id=request.vehicle_id,
    )
    
    return {
        "success": True,
        "plan": plan,
    }


@router.post("/mission/{plan_id}/start", tags=["Mission Planner"])
async def start_mission(plan_id: str, request: StartMissionRequest):
    """
    Start a mission from a plan.
    
    Assigns a vehicle and begins the journey.
    """
    planner = MissionPlanner()
    store = get_store()
    
    # Check vehicle exists and is available
    vehicle = store.get_vehicle(request.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle["status"] != "available":
        raise HTTPException(status_code=400, detail="Vehicle is not available")
    
    # For demo, create a quick plan if plan_id is "new"
    if plan_id == "new":
        raise HTTPException(
            status_code=400, 
            detail="Please first call /mission/plan to create a plan"
        )
    
    # Note: In a full implementation, we would retrieve the saved plan
    # For demo, accept any plan_id and create a new mission
    return {
        "success": True,
        "message": "Mission started",
        "vehicle_id": request.vehicle_id,
    }


@router.get("/mission/{mission_id}", tags=["Mission Planner"])
async def get_mission(mission_id: str):
    """Get mission details by ID."""
    store = get_store()
    mission = store.get_mission(mission_id)
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return {
        "success": True,
        "mission": mission,
    }


@router.get("/missions", tags=["Mission Planner"])
async def list_missions(status: Optional[str] = None):
    """List all missions, optionally filtered by status."""
    store = get_store()
    missions = store.get_all_missions(status=status)
    
    return {
        "success": True,
        "count": len(missions),
        "missions": missions,
    }


@router.patch("/mission/{mission_id}/status", tags=["Mission Planner"])
async def update_mission_status(mission_id: str, status: str):
    """Update mission status."""
    store = get_store()
    
    if status == "completed":
        mission = store.complete_mission(mission_id)
    else:
        mission = store.update_mission(mission_id, {"status": status})
    
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    return {
        "success": True,
        "mission": mission,
    }


# ==========================================
# MODULE 2: DECISION ENGINE
# ==========================================

@router.post("/decision/evaluate", tags=["Decision Engine"])
async def evaluate_situation(request: EvaluateSituationRequest):
    """
    Evaluate the current situation and get AI recommendation.
    
    **Module 2: Rolling Decision Engine**
    
    This is the main Observe → Reason → Decide loop:
    - Observes current conditions (traffic, weather, etc.)
    - Uses AI to reason about the situation
    - Decides on best action (continue, reroute, stop, alert)
    """
    engine = DecisionEngine()
    
    result = await engine.evaluate_situation(
        mission_id=request.mission_id,
        current_location=request.current_location,
        current_conditions=request.conditions,
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "success": True,
        "evaluation": result,
    }


@router.post("/decision/opportunity", tags=["Decision Engine"])
async def evaluate_opportunity(request: EvaluateOpportunityRequest):
    """
    Evaluate if a specific opportunity is worth pursuing.
    
    Uses "Opportunity vs. Cost" calculation to determine
    if deviating from the plan is profitable.
    """
    engine = DecisionEngine()
    
    result = await engine.evaluate_opportunity(
        mission_id=request.mission_id,
        opportunity=request.opportunity,
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "success": True,
        "evaluation": result,
    }


@router.post("/decision/reroute", tags=["Decision Engine"])
async def get_reroute_options(request: RerouteRequest):
    """
    Get alternative route options when conditions change.
    
    Returns multiple route alternatives with pros/cons.
    """
    engine = DecisionEngine()
    
    result = await engine.get_reroute_options(
        mission_id=request.mission_id,
        reason=request.reason,
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "success": True,
        "reroute_options": result,
    }


@router.get("/decision/{mission_id}/history", tags=["Decision Engine"])
async def get_decision_history(mission_id: str):
    """Get the decision log for a mission."""
    store = get_store()
    
    mission = store.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    history = store.get_decision_log(mission_id)
    
    return {
        "success": True,
        "mission_id": mission_id,
        "decision_count": len(history),
        "history": history,
    }


# ==========================================
# COPILOT CHAT
# ==========================================

@router.post("/copilot/chat", tags=["Copilot"])
async def copilot_chat(request: CopilotChatRequest):
    """
    AI Copilot chat endpoint for natural language driver assistance.
    
    Uses Gemini AI to respond to driver queries with mission context.
    """
    store = get_store()
    gemini = get_gemini_client()
    
    # Get mission context
    mission = store.get_mission(request.mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    
    # Build context for AI
    mission_context = f"""
Current Mission Context:
- Route: {mission.get('origin', 'Unknown')} → {mission.get('destination', 'Unknown')}
- Progress: {mission.get('progress_percent', 0)}% complete
- Current Location: {mission.get('current_location', mission.get('origin', 'Unknown'))}
- Cargo: {mission.get('cargo', {}).get('type', 'General')} - {mission.get('cargo', {}).get('weight_tons', 0)} tons
- Distance: {mission.get('route', {}).get('distance_km', 0)} km total
- ETA: {mission.get('eta_range', {}).get('expected', {}).get('hours', 0)} hours expected

Current Conditions (simulated):
- Traffic: Moderate
- Weather: Clear
- Fuel Level: 75%
- Driver Status: Active for 3.5 hours
"""
    
    # Create prompt for Gemini
    prompt = f"""You are an AI Copilot assistant for a truck driver on an Indian logistics route.
Be helpful, concise, and practical. Use relevant emojis to make responses friendly.

{mission_context}

Driver's Query: "{request.query}"

Provide a helpful, actionable response. If they ask about:
- Traffic: Give realistic traffic update for Indian highways
- Fuel: Recommend nearest fuel stop with estimated distance and price
- Weather: Provide weather conditions and forecast
- Rest/Fatigue: Recommend safe rest stops and break timing
- Opportunities/Loads: Mention any available LTL loads or revenue opportunities
- Route/Navigation: Provide route guidance and checkpoints

Keep response under 150 words. Be specific and helpful."""

    try:
        # Generate response with Gemini
        response = gemini.generate_content(prompt)
        ai_response = response.text.strip() if response.text else "I'm here to help! What would you like to know about your route?"
    except Exception as e:
        # Fallback response if AI fails
        ai_response = f"I'm analyzing your route... Based on current conditions, everything looks good. How can I assist you further? 🛣️"
    
    return {
        "success": True,
        "mission_id": request.mission_id,
        "query": request.query,
        "response": ai_response,
        "context": {
            "progress": mission.get('progress_percent', 0),
            "location": mission.get('current_location', mission.get('origin')),
            "destination": mission.get('destination'),
        }
    }


# ==========================================
# MODULE 3: CAPACITY MANAGER
# ==========================================

@router.post("/capacity/ltl-matches", tags=["Capacity Manager"])
async def find_ltl_matches(request: FindLTLRequest):
    """
    Find LTL loads to fill unused truck capacity.
    
    **Module 3: Dynamic Capacity Manager - En-Route Pooling**
    
    Scans for "gap-filler" loads along the current route
    that can be added to increase revenue per mile.
    """
    manager = CapacityManager()
    
    result = await manager.find_ltl_matches(
        mission_id=request.mission_id,
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "success": True,
        "ltl_matches": result,
    }


@router.post("/capacity/backhaul", tags=["Capacity Manager"])
async def find_backhaul(request: FindBackhaulRequest):
    """
    Find return load options to avoid empty trips.
    
    **Module 3: Dynamic Capacity Manager - Predictive Backhauling**
    
    Pre-negotiates return loads before reaching destination,
    ensuring zero "deadhead" (empty) miles on the way back.
    """
    manager = CapacityManager()
    
    result = await manager.find_backhaul(
        mission_id=request.mission_id,
        home_base=request.home_base,
    )
    
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {
        "success": True,
        "backhaul_options": result,
    }


@router.post("/capacity/pool", tags=["Capacity Manager"])
async def accept_ltl_load(request: AcceptLoadRequest):
    """
    Accept an LTL load to pool with current mission.
    
    Adds the load to the truck, updating capacity utilization.
    """
    manager = CapacityManager()
    
    result = await manager.accept_ltl_load(
        mission_id=request.mission_id,
        load_id=request.load_id,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.post("/capacity/book-backhaul", tags=["Capacity Manager"])
async def book_backhaul(request: BookBackhaulRequest):
    """
    Book a backhaul load for the return journey.
    
    Locks in the return load before completing current delivery.
    """
    manager = CapacityManager()
    
    result = await manager.book_backhaul(
        mission_id=request.mission_id,
        backhaul_load_id=request.load_id,
    )
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


@router.get("/capacity/overview", tags=["Capacity Manager"])
async def get_capacity_overview():
    """
    Get overall fleet capacity utilization.
    
    Shows utilization across all active missions with recommendations.
    """
    manager = CapacityManager()
    
    result = await manager.get_capacity_overview()
    
    return {
        "success": True,
        "overview": result,
    }


# ==========================================
# UTILITY ENDPOINTS
# ==========================================

@router.get("/routes", tags=["Data"])
async def get_routes():
    """Get list of available routes."""
    cities = get_all_cities()
    
    # Get popular routes
    popular = []
    for (origin, dest), info in list(INDIAN_ROUTES.items())[:10]:
        popular.append({
            "origin": origin,
            "destination": dest,
            "distance_km": info["distance_km"],
            "estimated_hours": info["base_hours"],
        })
    
    return {
        "success": True,
        "cities": cities,
        "popular_routes": popular,
    }


@router.get("/routes/{origin}/{destination}", tags=["Data"])
async def get_route_details(origin: str, destination: str):
    """Get route details between two cities."""
    route = get_route_info(origin, destination)
    
    return {
        "success": True,
        "route": route,
    }


@router.get("/loads", tags=["Data"])
async def get_loads(
    load_type: Optional[str] = None,
    max_weight: Optional[float] = None,
):
    """Get available loads in the market."""
    loads = get_available_loads(
        load_type=load_type,
        max_weight=max_weight,
    )
    
    return {
        "success": True,
        "count": len(loads),
        "loads": loads,
    }


@router.get("/vehicles", tags=["Data"])
async def get_vehicles(city: Optional[str] = None):
    """Get available vehicles."""
    store = get_store()
    vehicles = store.get_available_vehicles(city=city)
    
    return {
        "success": True,
        "count": len(vehicles),
        "vehicles": vehicles,
    }


@router.get("/vehicle/{vehicle_id}", tags=["Data"])
async def get_vehicle(vehicle_id: str):
    """Get vehicle details."""
    store = get_store()
    vehicle = store.get_vehicle(vehicle_id)
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    return {
        "success": True,
        "vehicle": vehicle,
    }


# ==========================================
# DEMO ENDPOINTS
# ==========================================

@router.get("/demo/scenario", tags=["Demo"])
async def get_demo_scenario():
    """
    Get a complete demo scenario for testing.
    
    Returns sample data to test all three modules.
    """
    store = get_store()
    
    # Create a demo mission if none exists
    missions = store.get_all_missions()
    if not missions:
        # Create a demo mission
        mission = store.create_mission({
            "origin": "Mumbai",
            "destination": "Delhi",
            "cargo": {
                "type": "Electronics",
                "weight_tons": 12,
            },
            "route": {
                "distance_km": 1420,
                "highways": ["NH48", "Mumbai-Agra Expressway"],
                "toll_plazas": 12,
                "toll_cost": 2800,
                "checkpoints": ["Rajasthan Border", "Gujarat Border", "Maharashtra Border"],
                "fuel_stops": 4,
            },
            "eta_range": {
                "optimistic": {"hours": 21.6},
                "expected": {"hours": 27.6},
                "pessimistic": {"hours": 36},
            },
            "fare": {
                "calculated": {
                    "total_fare": 85000,
                    "per_km_rate": 59.86,
                }
            },
            "risk_assessment": {
                "score": 35,
                "level": "medium",
                "factors": ["Long haul journey", "3 state border crossings"],
            },
            "vehicle_id": "v-001",
        })
        store.start_mission(mission["id"])
        store.update_mission(mission["id"], {
            "progress_percent": 35,
            "current_location": "Ahmedabad",
        })
        demo_mission = store.get_mission(mission["id"])
    else:
        demo_mission = missions[0]
    
    vehicle = store.get_vehicle("v-001")
    
    return {
        "success": True,
        "scenario": {
            "name": "Mumbai to Delhi Electronics Shipment",
            "description": "A 12-ton electronics shipment traveling via NH48. Currently at Ahmedabad (35% complete). Demonstrates all 3 modules.",
            "mission": demo_mission,
            "vehicle": vehicle,
            "test_endpoints": {
                "evaluate_situation": {
                    "url": "/api/decision/evaluate",
                    "method": "POST",
                    "body": {
                        "mission_id": demo_mission["id"],
                        "current_location": "Ahmedabad",
                    }
                },
                "find_ltl_matches": {
                    "url": "/api/capacity/ltl-matches",
                    "method": "POST",
                    "body": {
                        "mission_id": demo_mission["id"],
                    }
                },
                "find_backhaul": {
                    "url": "/api/capacity/backhaul",
                    "method": "POST",
                    "body": {
                        "mission_id": demo_mission["id"],
                        "home_base": "Mumbai",
                    }
                },
            },
            "sample_opportunity": {
                "id": "opp-001",
                "type": "ltl_pickup",
                "description": "Pickup 2 tons of auto parts from Ahmedabad, deliver to Jaipur",
                "revenue": 5500,
                "detour_km": 25,
            },
        }
    }


@router.post("/demo/reset", tags=["Demo"])
async def reset_demo_data():
    """Reset demo data to initial state."""
    global _store
    from app.data.store import DataStore
    
    # Re-initialize the store
    new_store = DataStore()
    
    # Replace the global instance
    import app.data.store as store_module
    store_module._store = new_store
    
    return {
        "success": True,
        "message": "Demo data reset successfully",
    }
