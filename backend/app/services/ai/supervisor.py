"""
Neuro-Logistics Supervisor Agent

A single AI agent that runs in a continuous decision loop and dynamically
switches behavior based on the truck's journey state.

The agent works as a smart co-pilot solving three pillars:
1. Smart Planning (Before Trip)
2. Live Adaptation (During Trip)  
3. Capacity & Return Optimization

Decision Loop: Observe → Reason → Decide → Act → Repeat
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import random
import json

from app.services.ai.grok_client import get_grok_client


class JourneyState(Enum):
    """Current state of the truck journey."""
    IDLE = "idle"                      # Truck is available, no mission
    PLANNING = "planning"              # Before trip - generating plan
    LOADING = "loading"                # At origin, loading cargo
    IN_TRANSIT = "in_transit"          # Actively moving
    AT_CHECKPOINT = "at_checkpoint"    # At toll/border checkpoint
    REFUELING = "refueling"            # At fuel stop
    UNLOADING = "unloading"            # At destination, unloading
    RETURNING = "returning"            # Return journey (empty or with backhaul)
    COMPLETED = "completed"            # Mission complete


class DecisionType(Enum):
    """Types of decisions the agent can make."""
    ROUTE_CHANGE = "route_change"
    ACCEPT_BACKHAUL = "accept_backhaul"
    REJECT_BACKHAUL = "reject_backhaul"
    ACCEPT_LTL_LOAD = "accept_ltl_load"
    FUEL_STOP = "fuel_stop"
    REST_STOP = "rest_stop"
    SPEED_ADJUSTMENT = "speed_adjustment"
    ETA_UPDATE = "eta_update"
    ALERT_DRIVER = "alert_driver"
    BOOK_RETURN_LOAD = "book_return_load"
    NO_ACTION = "no_action"


@dataclass
class TruckState:
    """Current state of the truck."""
    vehicle_id: str
    registration_number: str
    current_location: Dict[str, float]  # lat, lng
    current_city: str
    speed_kmh: float
    fuel_level_percent: float
    max_capacity_tons: float
    current_load_tons: float
    driver_name: str
    driver_hours_remaining: float  # Hours before mandatory rest
    last_update: str
    
    @property
    def available_capacity_tons(self) -> float:
        return self.max_capacity_tons - self.current_load_tons
    
    @property
    def utilization_percent(self) -> float:
        return (self.current_load_tons / self.max_capacity_tons) * 100


@dataclass
class MissionState:
    """Current mission details."""
    mission_id: str
    origin: str
    destination: str
    origin_address: str
    destination_address: str
    cargo_type: str
    weight_tons: float
    distance_km: float
    progress_km: float
    base_fare: float
    toll_cost: float
    fuel_cost_estimated: float
    started_at: str
    expected_arrival: str
    checkpoints: List[Dict[str, Any]]
    current_checkpoint_index: int
    
    @property
    def progress_percent(self) -> float:
        return (self.progress_km / self.distance_km) * 100 if self.distance_km > 0 else 0
    
    @property
    def remaining_km(self) -> float:
        return self.distance_km - self.progress_km


@dataclass
class EnvironmentState:
    """External environment factors."""
    weather_condition: str  # clear, rain, fog, storm
    traffic_level: str  # light, moderate, heavy, blocked
    road_condition: str  # good, fair, poor
    delay_probability: float  # 0-1, chance of delays
    current_fuel_price: float  # per liter
    toll_queue_minutes: int
    border_crossing_delay_minutes: int
    
    # Indian specific
    is_festival_season: bool
    is_strike_alert: bool
    connectivity_status: str  # good, poor, offline


@dataclass
class Observation:
    """Complete observation of current state."""
    timestamp: str
    journey_state: JourneyState
    truck: TruckState
    mission: Optional[MissionState]
    environment: EnvironmentState
    available_loads: List[Dict[str, Any]]  # Nearby loads for LTL/backhaul
    alerts: List[str]


@dataclass
class Reasoning:
    """Agent's reasoning process."""
    observations: List[str]
    constraints: List[str]
    opportunities: List[str]
    risks: List[str]
    trade_offs: List[str]
    recommendation: str
    confidence: float


@dataclass
class Decision:
    """Agent's decision."""
    decision_type: DecisionType
    action_details: Dict[str, Any]
    reasoning: Reasoning
    expected_benefit: Dict[str, Any]
    priority: str  # low, medium, high, critical
    timestamp: str


@dataclass
class AgentAction:
    """Action to be executed."""
    action_id: str
    decision: Decision
    execution_status: str  # pending, executing, completed, failed
    result: Optional[Dict[str, Any]] = None


class NeuroLogisticsSupervisor:
    """
    Main AI Agent that runs in a continuous decision loop.
    
    Handles all three modules:
    1. Smart Planning (Before Trip)
    2. Live Adaptation (During Trip)
    3. Capacity & Return Optimization
    """
    
    def __init__(self, truck_id: str):
        self.truck_id = truck_id
        self.current_state: JourneyState = JourneyState.IDLE
        self.observation_history: List[Observation] = []
        self.decision_history: List[Decision] = []
        self.action_queue: List[AgentAction] = []
        self.grok_client = None
        
        # Configuration
        self.config = {
            "min_profit_threshold": 500,  # INR
            "max_detour_km": 30,
            "max_detour_minutes": 45,
            "min_fuel_alert_percent": 25,
            "driver_rest_threshold_hours": 2,
            "eta_update_threshold_minutes": 30,
            "confidence_threshold": 0.7,
        }
    
    async def initialize(self):
        """Initialize the agent with AI client."""
        self.grok_client = get_grok_client()
    
    # ==========================================
    # MAIN DECISION LOOP
    # ==========================================
    
    async def run_decision_loop(
        self,
        truck_state: TruckState,
        mission_state: Optional[MissionState],
        environment: EnvironmentState,
        available_loads: List[Dict[str, Any]] = None
    ) -> Decision:
        """
        Main decision loop: Observe → Reason → Decide → Act
        
        This is the core of the Neuro-Logistics Supervisor.
        """
        # 1. OBSERVE - Gather all relevant information
        observation = self._observe(
            truck_state, 
            mission_state, 
            environment, 
            available_loads or []
        )
        self.observation_history.append(observation)
        
        # 2. REASON - Analyze the situation based on journey state
        reasoning = await self._reason(observation)
        
        # 3. DECIDE - Make a decision based on reasoning
        decision = self._decide(observation, reasoning)
        self.decision_history.append(decision)
        
        # 4. ACT - Queue the action for execution
        action = self._create_action(decision)
        self.action_queue.append(action)
        
        return decision
    
    # ==========================================
    # MODULE 1: SMART PLANNING (Before Trip)
    # ==========================================
    
    async def generate_smart_plan(
        self,
        truck: TruckState,
        origin: str,
        destination: str,
        cargo_type: str,
        weight_tons: float
    ) -> Dict[str, Any]:
        """
        Generate a smart trip plan before the journey.
        
        Features:
        - Realistic route (accounts for borders, restrictions, narrow roads)
        - Dynamic effort-based fare calculation
        - ETA range (not single optimistic time)
        """
        from app.services.maps import get_maps_service
        maps = get_maps_service()
        
        # Get base route
        route = maps.get_route(origin, destination)
        
        # Calculate Indian-context adjustments
        delay_factors = self._calculate_delay_factors(route, cargo_type)
        
        # Generate ETA range
        eta_range = self._calculate_eta_range(
            route.duration_hours,
            delay_factors
        )
        
        # Calculate dynamic fare
        fare = self._calculate_dynamic_fare(
            route, weight_tons, cargo_type, delay_factors
        )
        
        # Generate waypoints with probabilities
        waypoints = self._generate_smart_waypoints(route, truck)
        
        # AI-enhanced insights
        ai_insights = []
        if self.grok_client:
            try:
                analysis = await self.grok_client.analyze_mission(
                    origin=origin,
                    destination=destination,
                    cargo_type=cargo_type,
                    weight_tons=weight_tons,
                    vehicle_type=truck.registration_number[:2]  # State code
                )
                ai_insights = analysis.get("recommendations", [])
            except Exception:
                pass
        
        return {
            "mission_id": f"m-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "origin": origin,
            "destination": destination,
            "route": {
                "distance_km": route.distance_km,
                "highways": route.highways,
                "is_estimated": route.is_estimated,
            },
            "eta_range": eta_range,
            "fare": fare,
            "waypoints": waypoints,
            "delay_factors": delay_factors,
            "risk_assessment": self._assess_route_risks(route, delay_factors),
            "ai_insights": ai_insights,
            "pre_booked_return_loads": self._find_return_load_options(destination, origin),
        }
    
    def _calculate_delay_factors(self, route, cargo_type: str) -> Dict[str, Any]:
        """Calculate realistic delay probabilities for Indian roads."""
        base_delay = 0.15  # 15% base delay probability
        
        factors = {
            "toll_delays": len(route.tolls) * 5,  # 5 min per toll avg
            "border_delays": len(route.checkpoints) * 15,  # 15 min per border
            "traffic_probability": 0.3,  # 30% chance of traffic
            "breakdown_probability": 0.05,  # 5% chance
            "weather_delay_probability": 0.1,  # 10% chance
            "total_expected_delay_hours": 0,
        }
        
        # Cargo-specific delays
        if cargo_type.lower() in ["hazmat", "chemicals", "explosives"]:
            factors["border_delays"] *= 2  # Double for hazmat
        
        if cargo_type.lower() in ["perishable", "dairy", "produce"]:
            factors["priority_factor"] = 1.2  # Faster routing needed
        
        # Calculate total expected delay
        factors["total_expected_delay_hours"] = (
            (factors["toll_delays"] + factors["border_delays"]) / 60 +
            route.duration_hours * factors["traffic_probability"] * 0.2
        )
        
        return factors
    
    def _calculate_eta_range(
        self, 
        base_hours: float, 
        delay_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate ETA range instead of single optimistic time."""
        expected_delay = delay_factors["total_expected_delay_hours"]
        
        # Optimistic: Everything goes perfectly
        optimistic_hours = base_hours * 0.95
        
        # Expected: Normal conditions with typical delays
        expected_hours = base_hours + expected_delay
        
        # Pessimistic: Multiple delays compound
        pessimistic_hours = base_hours + expected_delay * 2.5
        
        now = datetime.now()
        
        return {
            "optimistic": {
                "hours": round(optimistic_hours, 1),
                "arrival": (now + timedelta(hours=optimistic_hours)).isoformat(),
            },
            "expected": {
                "hours": round(expected_hours, 1),
                "arrival": (now + timedelta(hours=expected_hours)).isoformat(),
            },
            "pessimistic": {
                "hours": round(pessimistic_hours, 1),
                "arrival": (now + timedelta(hours=pessimistic_hours)).isoformat(),
            },
            "confidence_interval": "80%",  # 80% chance within expected-pessimistic
        }
    
    def _calculate_dynamic_fare(
        self,
        route,
        weight_tons: float,
        cargo_type: str,
        delay_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate dynamic effort-based fare."""
        from app.services.maps import get_maps_service
        maps = get_maps_service()
        
        # Base fare from maps service
        toll_cost = sum(t["cost"] for t in route.tolls)
        base_fare = maps.calculate_fare(
            route.distance_km, weight_tons, "hcv", toll_cost
        )
        
        # Effort adjustments
        effort_multiplier = 1.0
        
        # Border crossings add effort
        effort_multiplier += len(route.checkpoints) * 0.02
        
        # Difficult cargo types
        if cargo_type.lower() in ["hazmat", "chemicals"]:
            effort_multiplier += 0.15
        elif cargo_type.lower() in ["fragile", "electronics"]:
            effort_multiplier += 0.10
        elif cargo_type.lower() in ["perishable"]:
            effort_multiplier += 0.12
        
        # Delay compensation
        effort_multiplier += delay_factors["total_expected_delay_hours"] * 0.02
        
        adjusted_base = base_fare["base_fare"] * effort_multiplier
        
        return {
            "base_fare": round(adjusted_base, 2),
            "toll_cost": toll_cost,
            "fuel_cost": base_fare["fuel_surcharge"],
            "effort_multiplier": round(effort_multiplier, 2),
            "delay_compensation": round(adjusted_base * 0.05, 2),
            "total_fare": round(
                adjusted_base + toll_cost + base_fare["fuel_surcharge"] + 
                base_fare["insurance"], 2
            ),
            "rate_per_km": round(adjusted_base / route.distance_km, 2),
            "breakdown": {
                "distance_km": route.distance_km,
                "weight_tons": weight_tons,
                "cargo_type": cargo_type,
                "border_crossings": len(route.checkpoints),
            }
        }
    
    def _generate_smart_waypoints(self, route, truck: TruckState) -> List[Dict[str, Any]]:
        """Generate waypoints with timing and recommendations."""
        waypoints = []
        cumulative_km = 0
        cumulative_hours = 0
        
        # Add fuel stops
        for stop in route.fuel_stops:
            cumulative_km = stop["km"]
            cumulative_hours = cumulative_km / 60  # Avg 60 km/h
            
            waypoints.append({
                "type": "fuel_stop",
                "name": stop["name"],
                "km": stop["km"],
                "estimated_arrival_hours": round(cumulative_hours, 1),
                "recommended_action": "Refuel if below 40%",
                "brand": stop.get("brand", "Unknown"),
            })
        
        # Add toll plazas
        for toll in route.tolls:
            waypoints.append({
                "type": "toll_plaza",
                "name": toll["name"],
                "km": toll["km"],
                "cost": toll["cost"],
                "estimated_wait_minutes": random.randint(5, 20),
            })
        
        # Add checkpoints
        for cp in route.checkpoints:
            waypoints.append({
                "type": "checkpoint",
                "name": cp["name"],
                "km": cp["km"],
                "checkpoint_type": cp.get("type", "state_border"),
                "estimated_delay_minutes": random.randint(10, 45),
                "documents_required": ["RC", "License", "E-Way Bill", "Insurance"],
            })
        
        # Sort by km
        waypoints.sort(key=lambda x: x["km"])
        
        return waypoints
    
    def _assess_route_risks(self, route, delay_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks for the route."""
        risk_score = 0
        risks = []
        
        # Distance risk
        if route.distance_km > 1000:
            risk_score += 15
            risks.append("Long haul journey (>1000 km)")
        
        # Border crossing risk
        if len(route.checkpoints) > 2:
            risk_score += 10 * len(route.checkpoints)
            risks.append(f"{len(route.checkpoints)} state border crossings")
        
        # Delay risk
        if delay_factors["total_expected_delay_hours"] > 3:
            risk_score += 20
            risks.append("High delay probability")
        
        return {
            "risk_score": min(risk_score, 100),
            "risk_level": "low" if risk_score < 30 else "medium" if risk_score < 60 else "high",
            "risk_factors": risks,
            "mitigation_suggestions": [
                "Keep all documents ready",
                "Maintain communication with dispatcher",
                "Plan rest stops in advance",
            ],
        }
    
    def _find_return_load_options(self, current_city: str, home_city: str) -> List[Dict[str, Any]]:
        """Find potential return load options to avoid dead miles."""
        # Mock return load options
        return [
            {
                "load_id": "rl-001",
                "shipper": "ABC Logistics",
                "pickup_city": current_city,
                "delivery_city": home_city,
                "cargo_type": "General Cargo",
                "weight_tons": 15,
                "offered_rate": 45000,
                "pickup_window": "Flexible",
                "pre_book_available": True,
            },
            {
                "load_id": "rl-002",
                "shipper": "XYZ Transport",
                "pickup_city": current_city,
                "delivery_city": home_city,
                "cargo_type": "Electronics",
                "weight_tons": 8,
                "offered_rate": 35000,
                "pickup_window": "2-4 hours after arrival",
                "pre_book_available": True,
            },
        ]
    
    # ==========================================
    # MODULE 2: LIVE ADAPTATION (During Trip)
    # ==========================================
    
    def _observe(
        self,
        truck: TruckState,
        mission: Optional[MissionState],
        environment: EnvironmentState,
        available_loads: List[Dict[str, Any]]
    ) -> Observation:
        """Observe current state of everything."""
        alerts = []
        
        # Generate alerts based on conditions
        if truck.fuel_level_percent < self.config["min_fuel_alert_percent"]:
            alerts.append(f"⚠️ Low fuel: {truck.fuel_level_percent}%")
        
        if truck.driver_hours_remaining < self.config["driver_rest_threshold_hours"]:
            alerts.append(f"⚠️ Driver rest needed in {truck.driver_hours_remaining}h")
        
        if environment.traffic_level == "heavy":
            alerts.append("🚗 Heavy traffic ahead")
        
        if environment.is_strike_alert:
            alerts.append("🚨 Strike alert in region")
        
        if environment.weather_condition in ["storm", "fog"]:
            alerts.append(f"🌧️ Adverse weather: {environment.weather_condition}")
        
        return Observation(
            timestamp=datetime.now().isoformat(),
            journey_state=self.current_state,
            truck=truck,
            mission=mission,
            environment=environment,
            available_loads=available_loads,
            alerts=alerts,
        )
    
    async def _reason(self, observation: Observation) -> Reasoning:
        """Reason about the current situation."""
        observations = []
        constraints = []
        opportunities = []
        risks = []
        trade_offs = []
        
        # Analyze truck state
        if observation.truck.fuel_level_percent < 30:
            observations.append(f"Fuel at {observation.truck.fuel_level_percent}%")
            constraints.append("Need to refuel within 100km")
        
        if observation.truck.available_capacity_tons > 5:
            observations.append(f"Unused capacity: {observation.truck.available_capacity_tons}T")
            opportunities.append("Can accept additional LTL loads")
        
        # Analyze mission
        if observation.mission:
            progress = observation.mission.progress_percent
            observations.append(f"Mission progress: {progress:.1f}%")
            
            if progress > 70:
                opportunities.append("Approaching destination - check return loads")
        
        # Analyze environment
        if observation.environment.traffic_level == "heavy":
            risks.append("Traffic may cause 30+ minute delay")
            trade_offs.append("Reroute adds 20km but saves 25 minutes")
        
        # Analyze available loads
        if observation.available_loads:
            for load in observation.available_loads:
                if load.get("match_score", 0) > 80:
                    opportunities.append(
                        f"High-match load available: {load.get('cargo_type')} "
                        f"({load.get('weight_tons')}T) - Score: {load.get('match_score')}"
                    )
        
        # Generate recommendation
        if opportunities and not constraints:
            recommendation = "Evaluate opportunities for additional earnings"
            confidence = 0.85
        elif constraints:
            recommendation = "Address constraints first, then evaluate opportunities"
            confidence = 0.9
        else:
            recommendation = "Continue current course"
            confidence = 0.95
        
        return Reasoning(
            observations=observations,
            constraints=constraints,
            opportunities=opportunities,
            risks=risks,
            trade_offs=trade_offs,
            recommendation=recommendation,
            confidence=confidence,
        )
    
    def _decide(self, observation: Observation, reasoning: Reasoning) -> Decision:
        """Make a decision based on reasoning."""
        decision_type = DecisionType.NO_ACTION
        action_details = {}
        priority = "low"
        expected_benefit = {}
        
        # Priority 1: Handle constraints (safety first)
        if reasoning.constraints:
            if "refuel" in str(reasoning.constraints).lower():
                decision_type = DecisionType.FUEL_STOP
                action_details = {
                    "action": "Navigate to nearest fuel station",
                    "urgency": "high",
                }
                priority = "high"
                expected_benefit = {"prevents_breakdown": True}
            
            elif "rest" in str(reasoning.constraints).lower():
                decision_type = DecisionType.REST_STOP
                action_details = {
                    "action": "Find safe rest stop",
                    "mandatory_rest_hours": 8,
                }
                priority = "critical"
                expected_benefit = {"compliance": True, "safety": True}
        
        # Priority 2: Handle risks
        elif reasoning.risks:
            if "traffic" in str(reasoning.risks).lower():
                decision_type = DecisionType.ROUTE_CHANGE
                action_details = {
                    "action": "Evaluate alternate route",
                    "potential_time_saved_minutes": 25,
                }
                priority = "medium"
                expected_benefit = {"time_saved_minutes": 25}
        
        # Priority 3: Exploit opportunities
        elif reasoning.opportunities:
            for opp in reasoning.opportunities:
                if "return load" in opp.lower():
                    decision_type = DecisionType.BOOK_RETURN_LOAD
                    action_details = {
                        "action": "Pre-book return load",
                        "search_criteria": "Best rate within pickup window",
                    }
                    priority = "medium"
                    expected_benefit = {"earnings": 40000, "avoids_dead_miles": True}
                    break
                    
                elif "LTL" in opp or "capacity" in opp.lower():
                    decision_type = DecisionType.ACCEPT_LTL_LOAD
                    action_details = {
                        "action": "Evaluate nearby LTL loads",
                        "max_detour_km": self.config["max_detour_km"],
                    }
                    priority = "low"
                    expected_benefit = {"additional_earnings": 5000}
                    break
        
        return Decision(
            decision_type=decision_type,
            action_details=action_details,
            reasoning=reasoning,
            expected_benefit=expected_benefit,
            priority=priority,
            timestamp=datetime.now().isoformat(),
        )
    
    def _create_action(self, decision: Decision) -> AgentAction:
        """Create an action from decision."""
        return AgentAction(
            action_id=f"act-{datetime.now().strftime('%H%M%S%f')}",
            decision=decision,
            execution_status="pending",
        )
    
    # ==========================================
    # MODULE 3: CAPACITY & RETURN OPTIMIZATION
    # ==========================================
    
    def analyze_capacity_opportunity(
        self,
        truck: TruckState,
        mission: MissionState,
        nearby_loads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze opportunities to fill unused capacity."""
        available = truck.available_capacity_tons
        
        matching_loads = []
        for load in nearby_loads:
            weight = load.get("weight_tons", 0)
            if weight <= available:
                # Calculate profitability
                detour_km = load.get("detour_km", 0)
                offered_rate = load.get("offered_rate", 0)
                fuel_cost = detour_km * 8  # ~8 INR per km fuel
                time_cost = detour_km / 40 * 500  # Time value at 40kmph
                
                net_profit = offered_rate - fuel_cost - time_cost
                
                if net_profit > self.config["min_profit_threshold"]:
                    matching_loads.append({
                        **load,
                        "net_profit": net_profit,
                        "fuel_cost": fuel_cost,
                        "time_cost": time_cost,
                        "recommendation": "ACCEPT" if net_profit > 2000 else "CONSIDER",
                    })
        
        # Sort by profitability
        matching_loads.sort(key=lambda x: x["net_profit"], reverse=True)
        
        return {
            "available_capacity_tons": available,
            "utilization_before": truck.utilization_percent,
            "potential_utilization_after": min(100, truck.utilization_percent + 
                (matching_loads[0]["weight_tons"] / truck.max_capacity_tons * 100) 
                if matching_loads else 0),
            "matching_loads": matching_loads[:5],  # Top 5 options
            "best_option": matching_loads[0] if matching_loads else None,
            "total_potential_earnings": sum(l["net_profit"] for l in matching_loads[:3]),
        }
    
    def find_backhaul_opportunities(
        self,
        destination: str,
        home_base: str,
        truck: TruckState,
        completion_time: str
    ) -> Dict[str, Any]:
        """Find backhaul opportunities to avoid dead miles."""
        # This would query a loads database in production
        # For now, return mock opportunities
        
        opportunities = [
            {
                "load_id": "bh-001",
                "shipper": "Steel Authority of India",
                "cargo_type": "Steel Coils",
                "weight_tons": 22,
                "pickup_city": destination,
                "delivery_city": home_base,
                "offered_rate": 55000,
                "pickup_window": "4-8 hours after arrival",
                "match_score": 92,
                "recommendation": "STRONGLY RECOMMENDED",
                "benefits": [
                    "Eliminates dead miles",
                    f"Rate above market average",
                    "Pickup timing aligns with rest period",
                ],
            },
            {
                "load_id": "bh-002",
                "shipper": "Reliance Industries",
                "cargo_type": "Polymer Bags",
                "weight_tons": 18,
                "pickup_city": destination,
                "delivery_city": home_base,
                "offered_rate": 42000,
                "pickup_window": "Immediate",
                "match_score": 78,
                "recommendation": "RECOMMENDED",
                "benefits": [
                    "Quick turnaround",
                    "Lighter load, fuel efficient",
                ],
            },
        ]
        
        return {
            "destination": destination,
            "home_base": home_base,
            "expected_completion": completion_time,
            "opportunities": opportunities,
            "best_option": opportunities[0],
            "dead_mile_cost_if_empty": self._calculate_dead_mile_cost(destination, home_base),
            "recommendation": "Pre-book backhaul load to maximize earnings",
        }
    
    def _calculate_dead_mile_cost(self, origin: str, destination: str) -> Dict[str, Any]:
        """Calculate cost of returning empty."""
        from app.services.maps import get_maps_service
        maps = get_maps_service()
        
        try:
            route = maps.get_route(origin, destination)
            fuel_cost = route.distance_km * 8  # 8 INR per km
            toll_cost = sum(t["cost"] for t in route.tolls) * 0.6  # Empty vehicles pay less
            driver_cost = route.duration_hours * 150  # Driver cost per hour
            
            return {
                "distance_km": route.distance_km,
                "fuel_cost": fuel_cost,
                "toll_cost": toll_cost,
                "driver_cost": driver_cost,
                "total_loss": fuel_cost + toll_cost + driver_cost,
                "message": f"Returning empty costs ₹{fuel_cost + toll_cost + driver_cost:.0f}",
            }
        except Exception:
            return {"total_loss": 15000, "message": "Estimated loss for empty return"}
    
    # ==========================================
    # SERIALIZATION
    # ==========================================
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current agent state summary."""
        return {
            "truck_id": self.truck_id,
            "journey_state": self.current_state.value,
            "observations_count": len(self.observation_history),
            "decisions_count": len(self.decision_history),
            "pending_actions": len([a for a in self.action_queue if a.execution_status == "pending"]),
            "last_decision": asdict(self.decision_history[-1]) if self.decision_history else None,
        }


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def create_supervisor(truck_id: str) -> NeuroLogisticsSupervisor:
    """Factory function to create a supervisor agent."""
    return NeuroLogisticsSupervisor(truck_id)


# Store active supervisors
_active_supervisors: Dict[str, NeuroLogisticsSupervisor] = {}


def get_or_create_supervisor(truck_id: str) -> NeuroLogisticsSupervisor:
    """Get existing or create new supervisor for a truck."""
    if truck_id not in _active_supervisors:
        _active_supervisors[truck_id] = create_supervisor(truck_id)
    return _active_supervisors[truck_id]
