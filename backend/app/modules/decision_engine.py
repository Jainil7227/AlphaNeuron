"""
Module 2: Rolling Decision Engine

Solves: Variable Time & Inability to Adapt during trip.

Features:
- Continuous Monitoring Loop (re-evaluate trip conditions)
- Opportunity vs. Cost Calculator (simulate if deviations are profitable)
- Autonomous Rerouting (update route when calculation is positive)
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import random

from app.data.store import get_store
from app.data.mock_loads import get_ltl_loads_on_route
from app.core.gemini_client import get_gemini_client


class DecisionEngine:
    """
    Rolling Decision Engine
    
    The "Brain" of the system - always-on loop that re-evaluates trips.
    Implements: Observe → Reason → Decide → Act
    """
    
    def __init__(self):
        self.store = get_store()
        self.gemini = get_gemini_client()
    
    async def evaluate_situation(
        self,
        mission_id: str,
        current_location: str,
        current_conditions: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Main decision loop entry point.
        
        Observe → Reason → Decide
        
        Returns decision with recommended action.
        """
        # Get mission data
        mission = self.store.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        # Default conditions if not provided
        if current_conditions is None:
            current_conditions = self._generate_simulated_conditions()
        
        # Calculate progress
        progress = self._calculate_progress(mission, current_location)
        
        # OBSERVE: Gather all relevant information
        observation = {
            "mission_id": mission_id,
            "origin": mission["origin"],
            "destination": mission["destination"],
            "current_location": current_location,
            "progress_percent": progress,
            "elapsed_time": self._calculate_elapsed_time(mission),
            "conditions": current_conditions,
            "nearby_opportunities": self._find_nearby_opportunities(
                current_location, 
                mission["destination"],
                mission["cargo"]["weight_tons"]
            ),
        }
        
        # REASON: Use AI to analyze the situation
        ai_evaluation = await self.gemini.evaluate_situation(
            current_location=current_location,
            destination=mission["destination"],
            progress_percent=progress,
            current_conditions=current_conditions,
        )
        
        # DECIDE: Determine best action
        decision = self._make_decision(observation, ai_evaluation)
        
        # Log the decision
        self.store.log_decision(mission_id, {
            "observation": observation,
            "ai_evaluation": ai_evaluation,
            "decision": decision,
        })
        
        # Update mission progress
        self.store.update_mission(mission_id, {
            "progress_percent": progress,
            "current_location": current_location,
            "last_evaluation": datetime.now().isoformat(),
        })
        
        return {
            "mission_id": mission_id,
            "observation": observation,
            "ai_analysis": ai_evaluation,
            "decision": decision,
            "timestamp": datetime.now().isoformat(),
        }
    
    async def evaluate_opportunity(
        self,
        mission_id: str,
        opportunity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluate if a specific opportunity is worth pursuing.
        
        Uses "Opportunity vs. Cost" calculation.
        """
        mission = self.store.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        # Build current mission context
        mission_context = {
            "origin": mission["origin"],
            "destination": mission["destination"],
            "progress_percent": mission.get("progress_percent", 0),
            "current_location": mission.get("current_location", mission["origin"]),
            "cargo": mission["cargo"],
            "current_fare": mission["fare"]["calculated"]["total_fare"],
            "remaining_distance_km": self._estimate_remaining_distance(mission),
        }
        
        # Get AI evaluation
        ai_decision = await self.gemini.evaluate_opportunity(
            current_mission=mission_context,
            opportunity=opportunity,
        )
        
        # Calculate our own cost-benefit
        cost_benefit = self._calculate_cost_benefit(mission, opportunity)
        
        # Combine AI and calculated insights
        result = {
            "mission_id": mission_id,
            "opportunity": opportunity,
            "ai_recommendation": ai_decision,
            "calculated_analysis": cost_benefit,
            "final_recommendation": self._combine_recommendations(ai_decision, cost_benefit),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Log the decision
        self.store.log_decision(mission_id, {
            "type": "opportunity_evaluation",
            "opportunity": opportunity,
            "result": result,
        })
        
        return result
    
    async def get_reroute_options(
        self,
        mission_id: str,
        reason: str = "traffic",
    ) -> Dict[str, Any]:
        """
        Get alternative route options when conditions change.
        """
        mission = self.store.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        current_location = mission.get("current_location", mission["origin"])
        destination = mission["destination"]
        
        # Generate simulated alternative routes
        # In production, this would call actual routing APIs
        alternatives = self._generate_alternative_routes(
            current_location,
            destination,
            reason,
        )
        
        return {
            "mission_id": mission_id,
            "current_location": current_location,
            "destination": destination,
            "reroute_reason": reason,
            "current_route": mission["route"],
            "alternative_routes": alternatives,
            "recommendation": self._recommend_best_route(alternatives, reason),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_simulated_conditions(self) -> Dict[str, Any]:
        """Generate simulated current conditions for demo."""
        traffic_levels = ["light", "moderate", "heavy", "severe"]
        weather_conditions = ["clear", "cloudy", "light_rain", "heavy_rain", "fog"]
        
        return {
            "traffic": random.choice(traffic_levels),
            "weather": random.choice(weather_conditions),
            "fuel_level_percent": random.randint(30, 80),
            "driver_fatigue_level": random.choice(["fresh", "normal", "tired"]),
            "vehicle_condition": random.choice(["good", "good", "minor_issue"]),
            "time_of_day": datetime.now().strftime("%H:%M"),
            "road_condition": random.choice(["good", "good", "construction", "damaged"]),
        }
    
    def _calculate_progress(self, mission: Dict[str, Any], current_location: str) -> float:
        """Calculate trip progress percentage."""
        # If current location matches destination, we're done
        if current_location.lower() == mission["destination"].lower():
            return 100.0
        
        # If current location matches origin, we haven't started
        if current_location.lower() == mission["origin"].lower():
            return 0.0
        
        # Otherwise estimate based on time elapsed
        if mission.get("started_at"):
            started = datetime.fromisoformat(mission["started_at"])
            elapsed_hours = (datetime.now() - started).total_seconds() / 3600
            expected_hours = mission["eta_range"]["expected"]["hours"]
            progress = min(95, (elapsed_hours / expected_hours) * 100)
            return round(progress, 1)
        
        return mission.get("progress_percent", 0)
    
    def _calculate_elapsed_time(self, mission: Dict[str, Any]) -> Optional[str]:
        """Calculate elapsed time since mission start."""
        if not mission.get("started_at"):
            return None
        
        started = datetime.fromisoformat(mission["started_at"])
        elapsed = datetime.now() - started
        hours = elapsed.total_seconds() / 3600
        
        return f"{hours:.1f} hours"
    
    def _find_nearby_opportunities(
        self, 
        current_location: str,
        destination: str,
        current_weight: float,
    ) -> List[Dict[str, Any]]:
        """Find LTL opportunities near current location."""
        # Get vehicle capacity (assuming 25 ton HCV)
        available_capacity = 25 - current_weight
        
        if available_capacity < 1:
            return []  # No room for additional loads
        
        loads = get_ltl_loads_on_route(
            origin=current_location,
            destination=destination,
            available_capacity=available_capacity,
        )
        
        return loads[:5]  # Return top 5
    
    def _estimate_remaining_distance(self, mission: Dict[str, Any]) -> float:
        """Estimate remaining distance."""
        total_distance = mission["route"]["distance_km"]
        progress = mission.get("progress_percent", 0)
        remaining = total_distance * (100 - progress) / 100
        return round(remaining, 1)
    
    def _calculate_cost_benefit(
        self,
        mission: Dict[str, Any],
        opportunity: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate cost-benefit of taking an opportunity."""
        # Detour cost estimate
        detour_km = opportunity.get("detour_km", 20)
        fuel_cost = (detour_km / 3.5) * 90  # ₹90/L, 3.5 km/L
        time_cost = (detour_km / 40) * 150  # ₹150 per hour driver cost
        total_cost = fuel_cost + time_cost
        
        # Revenue from opportunity
        revenue = opportunity.get("offered_rate", 0)
        
        # Net benefit
        net_benefit = revenue - total_cost
        
        return {
            "detour_km": detour_km,
            "fuel_cost": round(fuel_cost),
            "time_cost": round(time_cost),
            "total_cost": round(total_cost),
            "revenue": revenue,
            "net_benefit": round(net_benefit),
            "profit_margin_percent": round((net_benefit / max(revenue, 1)) * 100, 1),
            "worth_taking": net_benefit > 500,  # Minimum ₹500 profit threshold
        }
    
    def _combine_recommendations(
        self,
        ai_decision: Dict[str, Any],
        cost_benefit: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Combine AI and calculated recommendations."""
        ai_recommends = ai_decision.get("recommendation", "CONSIDER") == "ACCEPT"
        calc_recommends = cost_benefit["worth_taking"]
        
        if ai_recommends and calc_recommends:
            final = "STRONGLY_ACCEPT"
            confidence = 90
            reason = "Both AI and cost analysis recommend taking this opportunity"
        elif ai_recommends or calc_recommends:
            final = "ACCEPT"
            confidence = 70
            reason = "Opportunity is beneficial based on one analysis"
        else:
            final = "REJECT"
            confidence = 80
            reason = "Neither AI nor cost analysis support this opportunity"
        
        return {
            "recommendation": final,
            "confidence": confidence,
            "reason": reason,
            "ai_vote": ai_recommends,
            "calc_vote": calc_recommends,
        }
    
    def _make_decision(
        self,
        observation: Dict[str, Any],
        ai_evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make final decision based on observation and AI analysis."""
        action = ai_evaluation.get("recommended_action", "CONTINUE")
        
        # Check for opportunities
        opportunities = observation.get("nearby_opportunities", [])
        high_value_opps = [o for o in opportunities if o.get("current_rate", 0) > 5000]
        
        # Check conditions
        conditions = observation.get("conditions", {})
        severe_conditions = (
            conditions.get("traffic") == "severe" or
            conditions.get("weather") in ["heavy_rain", "fog"] or
            conditions.get("driver_fatigue_level") == "tired"
        )
        
        # Build decision
        decision = {
            "action": action,
            "confidence": ai_evaluation.get("confidence", 70),
            "reasons": [],
            "alerts": [],
            "opportunities_found": len(opportunities),
        }
        
        # Add reasons and alerts
        if severe_conditions:
            decision["alerts"].append({
                "type": "warning",
                "message": "Adverse conditions detected. Consider stopping for rest.",
            })
        
        if high_value_opps:
            decision["alerts"].append({
                "type": "opportunity",
                "message": f"Found {len(high_value_opps)} high-value loads nearby!",
                "loads": [o["id"] for o in high_value_opps],
            })
        
        if action == "REROUTE":
            decision["reasons"].append("Traffic or road conditions suggest alternate route")
        elif action == "STOP":
            decision["reasons"].append("Rest recommended for safety")
        elif action == "ALERT":
            decision["reasons"].append("Situation requires driver attention")
        else:
            decision["reasons"].append("Conditions normal, continue as planned")
        
        return decision
    
    def _generate_alternative_routes(
        self,
        current_location: str,
        destination: str,
        reason: str,
    ) -> List[Dict[str, Any]]:
        """Generate simulated alternative routes."""
        # In production, this would call routing APIs
        # For demo, generate plausible alternatives
        
        base_time = random.randint(180, 360)  # 3-6 hours
        
        routes = [
            {
                "id": "alt-1",
                "name": "Highway Route",
                "via": "National Highway",
                "distance_km": random.randint(200, 350),
                "estimated_minutes": base_time,
                "toll_cost": random.randint(300, 800),
                "pros": ["Faster", "Better road condition"],
                "cons": ["Higher tolls", "More traffic"],
            },
            {
                "id": "alt-2",
                "name": "State Highway Route",
                "via": "State Highway",
                "distance_km": random.randint(220, 380),
                "estimated_minutes": base_time + 45,
                "toll_cost": random.randint(100, 400),
                "pros": ["Lower tolls", "Less congested"],
                "cons": ["Slightly longer", "Variable road quality"],
            },
            {
                "id": "alt-3",
                "name": "Mixed Route",
                "via": "NH + Local Roads",
                "distance_km": random.randint(180, 320),
                "estimated_minutes": base_time + 30,
                "toll_cost": random.randint(200, 500),
                "pros": ["Balanced option", "Avoids major traffic"],
                "cons": ["Some local road sections"],
            },
        ]
        
        return routes
    
    def _recommend_best_route(
        self,
        alternatives: List[Dict[str, Any]],
        reason: str,
    ) -> Dict[str, Any]:
        """Recommend the best route based on reason."""
        if not alternatives:
            return {"route_id": None, "reason": "No alternatives available"}
        
        if reason == "traffic":
            # Prefer routes that avoid traffic
            best = min(alternatives, key=lambda r: r["estimated_minutes"])
            return {
                "route_id": best["id"],
                "reason": "Fastest option to avoid traffic delays",
            }
        elif reason == "cost":
            # Prefer cheaper routes
            best = min(alternatives, key=lambda r: r["toll_cost"])
            return {
                "route_id": best["id"],
                "reason": "Most cost-effective option",
            }
        else:
            # Default to balanced option
            return {
                "route_id": alternatives[-1]["id"],  # Mixed route
                "reason": "Balanced option for overall efficiency",
            }
