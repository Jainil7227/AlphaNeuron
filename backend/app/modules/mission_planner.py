"""
Module 1: Context-Aware Mission Planner

Solves: Static Pricing & Route Rigidity at trip start.

Features:
- Infrastructure-Aware Routing (checkpost delays, no-entry timings)
- Dynamic Fare Engine (effort-based, not just distance)
- ETA Range (optimistic/expected/pessimistic)
- Risk Assessment
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from app.data.mock_routes import get_route_info
from app.data.mock_loads import get_backhaul_loads
from app.data.store import get_store
from app.core.gemini_client import get_gemini_client


class MissionPlanner:
    """
    Context-Aware Mission Planner
    
    Generates smart trip plans with dynamic pricing and realistic ETAs.
    """
    
    def __init__(self):
        self.store = get_store()
        self.gemini = get_gemini_client()
    
    async def plan_mission(
        self,
        origin: str,
        destination: str,
        cargo_type: str,
        weight_tons: float,
        vehicle_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive mission plan.
        
        Returns:
        - Route details with realistic timing
        - Dynamic fare calculation
        - Risk assessment
        - Pre-identified return load options
        """
        # Get base route info
        route = get_route_info(origin, destination)
        
        # Calculate dynamic fare
        fare = self._calculate_dynamic_fare(route, cargo_type, weight_tons)
        
        # Get AI-enhanced route analysis
        ai_analysis = await self.gemini.analyze_route(
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            weight_tons=weight_tons,
        )
        
        # Get AI-enhanced fare calculation
        ai_fare = await self.gemini.calculate_dynamic_fare(
            origin=origin,
            destination=destination,
            distance_km=route["distance_km"],
            cargo_type=cargo_type,
            weight_tons=weight_tons,
            risk_level=route.get("risk_level", "medium"),
        )
        
        # Calculate ETA range
        now = datetime.now()
        eta_range = {
            "optimistic": {
                "hours": route["eta_optimistic_hours"],
                "arrival": (now + timedelta(hours=route["eta_optimistic_hours"])).isoformat(),
            },
            "expected": {
                "hours": route["eta_expected_hours"],
                "arrival": (now + timedelta(hours=route["eta_expected_hours"])).isoformat(),
            },
            "pessimistic": {
                "hours": route["eta_pessimistic_hours"],
                "arrival": (now + timedelta(hours=route["eta_pessimistic_hours"])).isoformat(),
            },
        }
        
        # Risk assessment
        risk = self._assess_risk(route, cargo_type, weight_tons)
        
        # Find potential return loads
        return_loads = get_backhaul_loads(destination, origin)
        
        # Create mission plan
        plan = {
            "mission_id": None,  # Will be set when started
            "origin": origin,
            "destination": destination,
            "cargo": {
                "type": cargo_type,
                "weight_tons": weight_tons,
            },
            "route": {
                "distance_km": route["distance_km"],
                "highways": route["highways"],
                "toll_plazas": route["tolls"],
                "toll_cost": route["toll_cost"],
                "checkpoints": route["checkpoints"],
                "fuel_stops": route["fuel_stops"],
                "is_estimated": route.get("is_estimated", False),
            },
            "eta_range": eta_range,
            "fare": {
                "calculated": fare,
                "ai_recommended": ai_fare,
            },
            "risk_assessment": risk,
            "ai_insights": ai_analysis,
            "return_load_options": return_loads[:3],  # Top 3 options
            "created_at": datetime.now().isoformat(),
        }
        
        return plan
    
    def _calculate_dynamic_fare(
        self,
        route: Dict[str, Any],
        cargo_type: str,
        weight_tons: float,
    ) -> Dict[str, Any]:
        """
        Calculate dynamic fare based on effort, not just distance.
        
        Unlike static per-km pricing, this accounts for real-world difficulty.
        """
        distance = route["distance_km"]
        
        # Base rate: ₹50-70 per km depending on conditions
        base_rate_per_km = 55
        base_fare = distance * base_rate_per_km
        
        # Effort multiplier based on various factors
        effort_multiplier = 1.0
        
        # Weight factor
        if weight_tons > 20:
            effort_multiplier += 0.15
        elif weight_tons > 15:
            effort_multiplier += 0.10
        elif weight_tons > 10:
            effort_multiplier += 0.05
        
        # Checkpoint factor (state borders add complexity)
        checkpoints = len(route.get("checkpoints", []))
        effort_multiplier += checkpoints * 0.03
        
        # Cargo type factor
        cargo_factors = {
            "hazmat": 0.25,
            "chemicals": 0.20,
            "perishables": 0.15,
            "fragile": 0.12,
            "electronics": 0.10,
            "pharmaceuticals": 0.12,
            "general": 0.0,
            "steel": 0.05,
            "cement": 0.03,
        }
        effort_multiplier += cargo_factors.get(cargo_type.lower(), 0.05)
        
        # Risk factor
        risk_factors = {"low": 0.0, "medium": 0.05, "high": 0.12, "unknown": 0.08}
        effort_multiplier += risk_factors.get(route.get("risk_level", "medium"), 0.05)
        
        # Calculate fare components
        adjusted_base = base_fare * effort_multiplier
        toll_cost = route["toll_cost"]
        
        # Fuel cost estimate (diesel ~₹90/L, HCV ~3.5 km/L)
        fuel_cost = (distance / 3.5) * 90
        
        # Driver allowance
        driver_allowance = route["base_hours"] * 150  # ₹150 per hour
        
        # Total fare
        total_fare = adjusted_base + toll_cost + (fuel_cost * 0.3)  # 30% fuel surcharge
        
        return {
            "base_fare": round(base_fare),
            "effort_multiplier": round(effort_multiplier, 2),
            "adjusted_base": round(adjusted_base),
            "toll_cost": toll_cost,
            "fuel_estimate": round(fuel_cost),
            "driver_allowance": round(driver_allowance),
            "total_fare": round(total_fare),
            "per_km_rate": round(total_fare / distance, 2),
        }
    
    def _assess_risk(
        self,
        route: Dict[str, Any],
        cargo_type: str,
        weight_tons: float,
    ) -> Dict[str, Any]:
        """Assess risks for the mission."""
        risk_score = 0
        risk_factors = []
        
        # Distance risk
        if route["distance_km"] > 1000:
            risk_score += 15
            risk_factors.append("Long haul journey (>1000 km)")
        elif route["distance_km"] > 500:
            risk_score += 8
            risk_factors.append("Medium distance journey")
        
        # Border crossing risk
        checkpoints = len(route.get("checkpoints", []))
        if checkpoints > 3:
            risk_score += 20
            risk_factors.append(f"{checkpoints} state border crossings")
        elif checkpoints > 1:
            risk_score += 10
            risk_factors.append(f"{checkpoints} state border crossings")
        
        # Cargo risk
        high_risk_cargo = ["hazmat", "chemicals", "perishables", "pharmaceuticals"]
        if cargo_type.lower() in high_risk_cargo:
            risk_score += 15
            risk_factors.append(f"Sensitive cargo: {cargo_type}")
        
        # Weight risk
        if weight_tons > 22:
            risk_score += 10
            risk_factors.append("Heavy load (>22 tons)")
        
        # Base route risk
        route_risk = route.get("risk_level", "medium")
        if route_risk == "high":
            risk_score += 15
            risk_factors.append("High-risk corridor")
        
        # Determine overall level
        if risk_score < 25:
            level = "low"
        elif risk_score < 50:
            level = "medium"
        else:
            level = "high"
        
        return {
            "score": min(risk_score, 100),
            "level": level,
            "factors": risk_factors,
            "recommendations": self._get_risk_recommendations(risk_factors),
        }
    
    def _get_risk_recommendations(self, risk_factors: list) -> list:
        """Generate recommendations based on risk factors."""
        recommendations = [
            "Keep all documents ready (RC, License, E-Way Bill, Insurance)",
            "Maintain regular communication with dispatch",
        ]
        
        if any("border" in f.lower() for f in risk_factors):
            recommendations.append("Prepare for potential delays at state borders")
        
        if any("heavy" in f.lower() for f in risk_factors):
            recommendations.append("Drive cautiously on curves and inclines")
        
        if any("sensitive" in f.lower() or "perishable" in f.lower() for f in risk_factors):
            recommendations.append("Monitor cargo conditions regularly")
        
        if any("long haul" in f.lower() for f in risk_factors):
            recommendations.append("Plan mandatory rest stops every 4-5 hours")
        
        return recommendations
    
    async def start_mission(self, plan: Dict[str, Any], vehicle_id: str) -> Dict[str, Any]:
        """
        Start a mission from a plan.
        
        Creates mission in store and updates vehicle status.
        """
        # Create mission in store
        mission_data = {
            "origin": plan["origin"],
            "destination": plan["destination"],
            "cargo": plan["cargo"],
            "route": plan["route"],
            "eta_range": plan["eta_range"],
            "fare": plan["fare"],
            "risk_assessment": plan["risk_assessment"],
            "vehicle_id": vehicle_id,
            "progress_percent": 0,
            "current_location": plan["origin"],
        }
        
        mission = self.store.create_mission(mission_data)
        mission = self.store.start_mission(mission["id"])
        
        # Update vehicle status
        self.store.update_vehicle(vehicle_id, {
            "status": "on_mission",
            "current_mission_id": mission["id"],
            "current_load_tons": plan["cargo"]["weight_tons"],
        })
        
        return mission
