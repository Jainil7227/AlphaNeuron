"""
Module 3: Dynamic Capacity Manager

Solves: Empty Return Trips & Partial Capacity.

Features:
- En-Route LTL Pooling (fill unused capacity with gap-filler loads)
- Predictive Backhauling (pre-negotiate return loads before arrival)
- Capacity Optimization (maximize revenue per mile)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from app.data.store import get_store
from app.data.mock_loads import get_ltl_loads_on_route, get_backhaul_loads, get_available_loads
from app.core.gemini_client import get_gemini_client


class CapacityManager:
    """
    Dynamic Capacity Manager
    
    Treats the truck as a "Real-Time Marketplace" to maximize utilization.
    Ensures zero dead miles and optimal capacity usage.
    """
    
    def __init__(self):
        self.store = get_store()
        self.gemini = get_gemini_client()
    
    async def find_ltl_matches(
        self,
        mission_id: str,
    ) -> Dict[str, Any]:
        """
        Find LTL loads to fill unused capacity during the trip.
        
        This is the "En-Route Pooling" feature.
        """
        mission = self.store.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        vehicle = self.store.get_vehicle(mission.get("vehicle_id", ""))
        
        # Calculate available capacity
        total_capacity = vehicle.get("capacity_tons", 25) if vehicle else 25
        current_load = mission["cargo"]["weight_tons"]
        available_capacity = total_capacity - current_load
        
        if available_capacity < 0.5:
            return {
                "mission_id": mission_id,
                "available_capacity_tons": 0,
                "message": "Truck is at full capacity",
                "matches": [],
            }
        
        # Get current location and route
        current_location = mission.get("current_location", mission["origin"])
        destination = mission["destination"]
        
        # Find matching LTL loads
        local_matches = get_ltl_loads_on_route(
            origin=current_location,
            destination=destination,
            available_capacity=available_capacity,
        )
        
        # Get AI recommendations
        ai_matches = await self.gemini.find_ltl_matches(
            current_route=f"{current_location} to {destination}",
            available_capacity_tons=available_capacity,
            available_loads=local_matches,
        )
        
        # Calculate potential revenue increase
        total_potential = sum(l.get("current_rate", 0) for l in local_matches)
        
        # Build response
        capacity_after = 0
        if ai_matches.get("recommended_loads"):
            weight_added = sum(
                next((l["weight_tons"] for l in local_matches if l["id"] == r["load_id"]), 0)
                for r in ai_matches["recommended_loads"]
            )
            capacity_after = ((current_load + weight_added) / total_capacity) * 100
        
        return {
            "mission_id": mission_id,
            "current_route": f"{current_location} → {destination}",
            "capacity": {
                "total_tons": total_capacity,
                "current_load_tons": current_load,
                "available_tons": available_capacity,
                "utilization_percent": round((current_load / total_capacity) * 100, 1),
            },
            "available_loads": local_matches,
            "ai_recommendations": ai_matches,
            "summary": {
                "loads_found": len(local_matches),
                "total_potential_revenue": total_potential,
                "utilization_after_pooling": round(capacity_after, 1),
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    async def find_backhaul(
        self,
        mission_id: str,
        home_base: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Find return load options before reaching destination.
        
        This is the "Predictive Backhauling" feature.
        No more empty return trips!
        """
        mission = self.store.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        vehicle = self.store.get_vehicle(mission.get("vehicle_id", ""))
        
        destination = mission["destination"]
        origin = home_base or mission["origin"]
        capacity = vehicle.get("capacity_tons", 25) if vehicle else 25
        
        # Find backhaul options
        backhaul_options = get_backhaul_loads(destination, origin)
        
        # Get AI recommendation
        ai_recommendation = await self.gemini.find_backhaul(
            current_destination=destination,
            home_base=origin,
            truck_capacity_tons=capacity,
            available_loads=backhaul_options,
        )
        
        # Calculate cost of empty return
        from app.data.mock_routes import get_route_info
        return_route = get_route_info(destination, origin)
        
        empty_return_cost = self._calculate_empty_return_cost(
            return_route["distance_km"],
            return_route["toll_cost"],
        )
        
        return {
            "mission_id": mission_id,
            "current_destination": destination,
            "home_base": origin,
            "truck_capacity_tons": capacity,
            "return_journey": {
                "distance_km": return_route["distance_km"],
                "estimated_hours": return_route["estimated_hours"],
            },
            "empty_return_cost": empty_return_cost,
            "backhaul_options": backhaul_options,
            "ai_recommendation": ai_recommendation,
            "savings_summary": {
                "without_backhaul": -empty_return_cost["total"],
                "with_best_backhaul": (
                    backhaul_options[0]["offered_rate"] - empty_return_cost["total"]
                    if backhaul_options else 0
                ),
                "potential_profit": (
                    backhaul_options[0]["offered_rate"]
                    if backhaul_options else 0
                ),
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    async def accept_ltl_load(
        self,
        mission_id: str,
        load_id: str,
    ) -> Dict[str, Any]:
        """
        Accept an LTL load to pool with current mission.
        """
        mission = self.store.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        # Find the load
        all_loads = get_available_loads(load_type="ltl")
        load = next((l for l in all_loads if l["id"] == load_id), None)
        
        if not load:
            return {"error": f"Load {load_id} not found"}
        
        # Check capacity
        vehicle = self.store.get_vehicle(mission.get("vehicle_id", ""))
        total_capacity = vehicle.get("capacity_tons", 25) if vehicle else 25
        current_load = mission["cargo"]["weight_tons"]
        available = total_capacity - current_load
        
        if load["weight_tons"] > available:
            return {
                "error": "Insufficient capacity",
                "required": load["weight_tons"],
                "available": available,
            }
        
        # Add to mission
        pooled_loads = mission.get("pooled_loads", [])
        pooled_loads.append({
            "load_id": load_id,
            "shipper": load["shipper"],
            "cargo_type": load["cargo_type"],
            "weight_tons": load["weight_tons"],
            "pickup_city": load["pickup_city"],
            "delivery_city": load["delivery_city"],
            "rate": load.get("current_rate", load["offered_rate"]),
            "added_at": datetime.now().isoformat(),
        })
        
        new_total_weight = current_load + load["weight_tons"]
        
        self.store.update_mission(mission_id, {
            "pooled_loads": pooled_loads,
            "cargo": {
                **mission["cargo"],
                "total_weight_tons": new_total_weight,
            },
        })
        
        # Update vehicle
        if vehicle:
            self.store.update_vehicle(mission["vehicle_id"], {
                "current_load_tons": new_total_weight,
            })
        
        return {
            "success": True,
            "mission_id": mission_id,
            "load_added": {
                "id": load_id,
                "weight_tons": load["weight_tons"],
                "rate": load.get("current_rate", load["offered_rate"]),
            },
            "updated_capacity": {
                "total_tons": total_capacity,
                "current_load_tons": new_total_weight,
                "available_tons": total_capacity - new_total_weight,
                "utilization_percent": round((new_total_weight / total_capacity) * 100, 1),
            },
            "additional_revenue": load.get("current_rate", load["offered_rate"]),
            "timestamp": datetime.now().isoformat(),
        }
    
    async def book_backhaul(
        self,
        mission_id: str,
        backhaul_load_id: str,
    ) -> Dict[str, Any]:
        """
        Book a backhaul load for the return journey.
        """
        mission = self.store.get_mission(mission_id)
        if not mission:
            return {"error": "Mission not found"}
        
        # Find the load
        all_loads = get_available_loads(load_type="backhaul")
        load = next((l for l in all_loads if l["id"] == backhaul_load_id), None)
        
        if not load:
            return {"error": f"Backhaul load {backhaul_load_id} not found"}
        
        # Update mission with booked backhaul
        self.store.update_mission(mission_id, {
            "booked_backhaul": {
                "load_id": backhaul_load_id,
                "shipper": load["shipper"],
                "cargo_type": load["cargo_type"],
                "weight_tons": load["weight_tons"],
                "pickup_city": load["pickup_city"],
                "delivery_city": load["delivery_city"],
                "rate": load.get("current_rate", load["offered_rate"]),
                "pickup_window": load["pickup_window"],
                "booked_at": datetime.now().isoformat(),
            },
        })
        
        # Log decision
        self.store.log_decision(mission_id, {
            "type": "backhaul_booked",
            "load_id": backhaul_load_id,
            "revenue": load.get("current_rate", load["offered_rate"]),
        })
        
        return {
            "success": True,
            "mission_id": mission_id,
            "backhaul_booked": {
                "load_id": backhaul_load_id,
                "route": f"{load['pickup_city']} → {load['delivery_city']}",
                "cargo": load["cargo_type"],
                "weight_tons": load["weight_tons"],
                "revenue": load.get("current_rate", load["offered_rate"]),
                "pickup_window": load["pickup_window"],
            },
            "message": f"Return load booked! Pickup at {load['pickup_city']} after current delivery.",
            "timestamp": datetime.now().isoformat(),
        }
    
    async def get_capacity_overview(
        self,
        vehicle_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get overall capacity utilization overview.
        """
        # Get all active missions
        active_missions = self.store.get_all_missions(status="in_progress")
        
        total_capacity = 0
        total_used = 0
        missions_data = []
        
        for mission in active_missions:
            vehicle = self.store.get_vehicle(mission.get("vehicle_id", ""))
            v_capacity = vehicle.get("capacity_tons", 25) if vehicle else 25
            v_load = mission["cargo"]["weight_tons"]
            
            # Add pooled loads
            pooled = mission.get("pooled_loads", [])
            pooled_weight = sum(p["weight_tons"] for p in pooled)
            total_load = v_load + pooled_weight
            
            total_capacity += v_capacity
            total_used += total_load
            
            missions_data.append({
                "mission_id": mission["id"],
                "route": f"{mission['origin']} → {mission['destination']}",
                "capacity_tons": v_capacity,
                "load_tons": total_load,
                "utilization_percent": round((total_load / v_capacity) * 100, 1),
                "pooled_loads": len(pooled),
                "has_backhaul": bool(mission.get("booked_backhaul")),
            })
        
        overall_utilization = (
            round((total_used / total_capacity) * 100, 1) 
            if total_capacity > 0 else 0
        )
        
        return {
            "total_active_missions": len(active_missions),
            "fleet_capacity": {
                "total_tons": total_capacity,
                "used_tons": total_used,
                "available_tons": total_capacity - total_used,
                "utilization_percent": overall_utilization,
            },
            "missions": missions_data,
            "recommendations": self._generate_capacity_recommendations(missions_data),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _calculate_empty_return_cost(
        self,
        distance_km: float,
        toll_cost: float,
    ) -> Dict[str, Any]:
        """Calculate the cost of driving empty (dead miles)."""
        # Fuel cost
        fuel_cost = (distance_km / 3.5) * 90  # ~3.5 km/L, ₹90/L
        
        # Driver cost
        hours = distance_km / 50  # ~50 km/h average
        driver_cost = hours * 150  # ₹150/hour
        
        # Wear and tear
        wear_cost = distance_km * 2  # ₹2/km maintenance reserve
        
        total = fuel_cost + toll_cost + driver_cost + wear_cost
        
        return {
            "fuel_cost": round(fuel_cost),
            "toll_cost": toll_cost,
            "driver_cost": round(driver_cost),
            "wear_cost": round(wear_cost),
            "total": round(total),
            "per_km": round(total / max(distance_km, 1), 2),
            "message": f"Driving empty costs ₹{round(total)} - find a backhaul load!",
        }
    
    def _generate_capacity_recommendations(
        self,
        missions_data: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Generate recommendations for capacity optimization."""
        recommendations = []
        
        for mission in missions_data:
            utilization = mission["utilization_percent"]
            
            if utilization < 50:
                recommendations.append({
                    "mission_id": mission["mission_id"],
                    "type": "low_utilization",
                    "severity": "high",
                    "message": f"Only {utilization}% capacity used. Find LTL loads to pool!",
                    "action": "find_ltl_matches",
                })
            elif utilization < 75:
                recommendations.append({
                    "mission_id": mission["mission_id"],
                    "type": "moderate_utilization",
                    "severity": "medium",
                    "message": f"{utilization}% capacity used. Consider adding small loads.",
                    "action": "find_ltl_matches",
                })
            
            if not mission.get("has_backhaul"):
                recommendations.append({
                    "mission_id": mission["mission_id"],
                    "type": "no_backhaul",
                    "severity": "high",
                    "message": "No return load booked. Avoid dead miles!",
                    "action": "find_backhaul",
                })
        
        return recommendations
