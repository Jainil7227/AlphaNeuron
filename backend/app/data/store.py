"""
In-Memory Data Store

Simple Python dictionaries to store active missions and vehicles.
Data resets on server restart - acceptable for hackathon demo.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class DataStore:
    """In-memory data store for missions and vehicles."""
    
    def __init__(self):
        self.missions: Dict[str, Dict[str, Any]] = {}
        self.vehicles: Dict[str, Dict[str, Any]] = {}
        self.decision_logs: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize with sample data
        self._seed_data()
    
    def _seed_data(self):
        """Seed with sample demo data."""
        # Sample vehicle
        self.vehicles["v-001"] = {
            "id": "v-001",
            "registration": "MH12AB1234",
            "type": "HCV",
            "capacity_tons": 25,
            "current_load_tons": 0,
            "driver_name": "Rajesh Kumar",
            "driver_phone": "+91-9876543210",
            "current_city": "Mumbai",
            "status": "available",
            "fuel_level_percent": 80,
            "created_at": datetime.now().isoformat(),
        }
        
        self.vehicles["v-002"] = {
            "id": "v-002",
            "registration": "DL14CD5678",
            "type": "HCV",
            "capacity_tons": 20,
            "current_load_tons": 0,
            "driver_name": "Suresh Yadav",
            "driver_phone": "+91-9876543211",
            "current_city": "Delhi",
            "status": "available",
            "fuel_level_percent": 65,
            "created_at": datetime.now().isoformat(),
        }
    
    # ==========================================
    # MISSION OPERATIONS
    # ==========================================
    
    def create_mission(self, mission_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new mission."""
        mission_id = f"m-{uuid.uuid4().hex[:8]}"
        
        mission = {
            "id": mission_id,
            "status": "planned",
            "created_at": datetime.now().isoformat(),
            "started_at": None,
            "completed_at": None,
            **mission_data,
        }
        
        self.missions[mission_id] = mission
        self.decision_logs[mission_id] = []
        
        return mission
    
    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get mission by ID."""
        return self.missions.get(mission_id)
    
    def update_mission(self, mission_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update mission fields."""
        if mission_id not in self.missions:
            return None
        
        self.missions[mission_id].update(updates)
        self.missions[mission_id]["updated_at"] = datetime.now().isoformat()
        
        return self.missions[mission_id]
    
    def start_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Start a mission."""
        return self.update_mission(mission_id, {
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
        })
    
    def complete_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        """Complete a mission."""
        return self.update_mission(mission_id, {
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
        })
    
    def get_all_missions(self, status: str = None) -> List[Dict[str, Any]]:
        """Get all missions, optionally filtered by status."""
        missions = list(self.missions.values())
        if status:
            missions = [m for m in missions if m["status"] == status]
        return missions
    
    # ==========================================
    # VEHICLE OPERATIONS
    # ==========================================
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Dict[str, Any]]:
        """Get vehicle by ID."""
        return self.vehicles.get(vehicle_id)
    
    def update_vehicle(self, vehicle_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update vehicle fields."""
        if vehicle_id not in self.vehicles:
            return None
        
        self.vehicles[vehicle_id].update(updates)
        return self.vehicles[vehicle_id]
    
    def get_available_vehicles(self, city: str = None) -> List[Dict[str, Any]]:
        """Get available vehicles, optionally filtered by city."""
        vehicles = [v for v in self.vehicles.values() if v["status"] == "available"]
        if city:
            city = city.strip().title()
            vehicles = [v for v in vehicles if v["current_city"] == city]
        return vehicles
    
    # ==========================================
    # DECISION LOG OPERATIONS
    # ==========================================
    
    def log_decision(self, mission_id: str, decision: Dict[str, Any]):
        """Log an AI decision for a mission."""
        if mission_id not in self.decision_logs:
            self.decision_logs[mission_id] = []
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            **decision,
        }
        self.decision_logs[mission_id].append(log_entry)
    
    def get_decision_log(self, mission_id: str) -> List[Dict[str, Any]]:
        """Get decision log for a mission."""
        return self.decision_logs.get(mission_id, [])


# Singleton instance
_store: Optional[DataStore] = None


def get_store() -> DataStore:
    """Get or create data store singleton."""
    global _store
    if _store is None:
        _store = DataStore()
    return _store
