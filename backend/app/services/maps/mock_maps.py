"""
Mock Maps Service for Indian Cities.

Provides route calculation, distance estimation, and fare calculation
without requiring any external APIs like Google Maps.

Contains pre-defined data for major Indian logistics routes.
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from dataclasses import dataclass
import math


class GeoPoint(BaseModel):
    """Geographic coordinates."""
    latitude: float
    longitude: float
    
    def model_dump(self) -> Dict[str, float]:
        return {"latitude": self.latitude, "longitude": self.longitude}


class RouteInfo(BaseModel):
    """Route information between two points."""
    origin: str
    destination: str
    distance_km: float
    duration_hours: float
    polyline: List[Dict[str, float]]
    tolls: List[Dict[str, Any]]
    fuel_stops: List[Dict[str, Any]]
    checkpoints: List[Dict[str, Any]]
    highways: List[str]
    is_estimated: bool = False


# Pre-defined city coordinates (major Indian cities)
CITY_COORDINATES: Dict[str, Tuple[float, float]] = {
    # Metro Cities
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Hyderabad": (17.3850, 78.4867),
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    
    # Major Logistics Hubs
    "Jaipur": (26.9124, 75.7873),
    "Lucknow": (26.8467, 80.9462),
    "Nagpur": (21.1458, 79.0882),
    "Surat": (21.1702, 72.8311),
    "Indore": (22.7196, 75.8577),
    "Vadodara": (22.3072, 73.1812),
    "Nashik": (19.9975, 73.7898),
    "Rajkot": (22.3039, 70.8022),
    "Coimbatore": (11.0168, 76.9558),
    "Visakhapatnam": (17.6868, 83.2185),
    
    # Industrial & Port Cities
    "Kandla": (23.0333, 70.2167),
    "Mundra": (22.8394, 69.7219),
    "JNPT": (18.9500, 72.9500),
    "Hazira": (21.1167, 72.6500),
    "Goa": (15.2993, 74.1240),
    "Cochin": (9.9312, 76.2673),
    "Mangalore": (12.9141, 74.8560),
    "Tuticorin": (8.7642, 78.1348),
    
    # North India
    "Chandigarh": (30.7333, 76.7794),
    "Amritsar": (31.6340, 74.8723),
    "Ludhiana": (30.9010, 75.8573),
    "Jalandhar": (31.3260, 75.5762),
    "Panipat": (29.3909, 76.9635),
    "Sonipat": (28.9288, 77.0913),
    "Gurgaon": (28.4595, 77.0266),
    "Noida": (28.5355, 77.3910),
    "Ghaziabad": (28.6692, 77.4538),
    
    # West India
    "Vapi": (20.3713, 72.9052),
    "Silvassa": (20.2766, 73.0089),
    "Daman": (20.4143, 72.8478),
    
    # South India
    "Mysore": (12.2958, 76.6394),
    "Hubli": (15.3647, 75.1240),
    "Belgaum": (15.8497, 74.4977),
    "Salem": (11.6643, 78.1460),
    "Madurai": (9.9252, 78.1198),
    "Trichy": (10.7905, 78.7047),
    
    # East India
    "Patna": (25.5941, 85.1376),
    "Ranchi": (23.3441, 85.3096),
    "Jamshedpur": (22.8046, 86.2029),
    "Bhubaneswar": (20.2961, 85.8245),
    "Cuttack": (20.4625, 85.8830),
    "Guwahati": (26.1445, 91.7362),
}


# Pre-defined routes with accurate data
PREDEFINED_ROUTES: Dict[str, Dict[str, Any]] = {
    "Delhi-Mumbai": {
        "distance_km": 1420,
        "duration_hours": 24,
        "highways": ["NH48", "NH44"],
        "tolls": [
            {"name": "Manesar Toll", "cost": 135, "km": 35},
            {"name": "Dharuhera Toll", "cost": 90, "km": 55},
            {"name": "Shahjahanpur Toll", "cost": 145, "km": 110},
            {"name": "Jaipur Bypass", "cost": 110, "km": 270},
            {"name": "Bhilwara Toll", "cost": 95, "km": 450},
            {"name": "Udaipur Toll", "cost": 120, "km": 600},
            {"name": "Ahmedabad Entry", "cost": 150, "km": 940},
            {"name": "Vadodara Toll", "cost": 105, "km": 1040},
            {"name": "Surat Toll", "cost": 135, "km": 1200},
            {"name": "Mumbai Entry", "cost": 180, "km": 1400},
        ],
        "fuel_stops": [
            {"name": "HP Manesar", "km": 35, "brand": "HP"},
            {"name": "IOCL Jaipur", "km": 270, "brand": "Indian Oil"},
            {"name": "BP Udaipur", "km": 600, "brand": "BP"},
            {"name": "Reliance Ahmedabad", "km": 940, "brand": "Reliance"},
            {"name": "Shell Surat", "km": 1200, "brand": "Shell"},
        ],
        "checkpoints": [
            {"name": "Rajasthan Border", "km": 200, "type": "state_border"},
            {"name": "Gujarat Border", "km": 850, "type": "state_border"},
            {"name": "Maharashtra Border", "km": 1300, "type": "state_border"},
        ],
    },
    "Mumbai-Bangalore": {
        "distance_km": 980,
        "duration_hours": 16,
        "highways": ["NH48", "NH44"],
        "tolls": [
            {"name": "Pune Expressway Entry", "cost": 265, "km": 15},
            {"name": "Khandala Toll", "cost": 95, "km": 80},
            {"name": "Satara Toll", "cost": 110, "km": 250},
            {"name": "Kolhapur Toll", "cost": 125, "km": 400},
            {"name": "Belgaum Toll", "cost": 140, "km": 510},
            {"name": "Hubli Toll", "cost": 95, "km": 650},
            {"name": "Davangere Toll", "cost": 105, "km": 780},
            {"name": "Tumkur Toll", "cost": 120, "km": 920},
        ],
        "fuel_stops": [
            {"name": "HP Lonavala", "km": 80, "brand": "HP"},
            {"name": "IOCL Satara", "km": 250, "brand": "Indian Oil"},
            {"name": "BP Belgaum", "km": 510, "brand": "BP"},
            {"name": "Shell Hubli", "km": 650, "brand": "Shell"},
        ],
        "checkpoints": [
            {"name": "Maharashtra-Karnataka Border", "km": 480, "type": "state_border"},
        ],
    },
    "Delhi-Kolkata": {
        "distance_km": 1530,
        "duration_hours": 26,
        "highways": ["NH19", "NH2"],
        "tolls": [
            {"name": "Faridabad Toll", "cost": 95, "km": 30},
            {"name": "Agra Toll", "cost": 145, "km": 200},
            {"name": "Kanpur Toll", "cost": 130, "km": 450},
            {"name": "Varanasi Toll", "cost": 155, "km": 800},
            {"name": "Patna Toll", "cost": 120, "km": 1000},
            {"name": "Dhanbad Toll", "cost": 110, "km": 1300},
            {"name": "Durgapur Toll", "cost": 140, "km": 1450},
        ],
        "fuel_stops": [
            {"name": "IOCL Agra", "km": 200, "brand": "Indian Oil"},
            {"name": "HP Kanpur", "km": 450, "brand": "HP"},
            {"name": "BP Varanasi", "km": 800, "brand": "BP"},
            {"name": "Reliance Dhanbad", "km": 1300, "brand": "Reliance"},
        ],
        "checkpoints": [
            {"name": "UP Border", "km": 80, "type": "state_border"},
            {"name": "Bihar Border", "km": 900, "type": "state_border"},
            {"name": "Jharkhand Border", "km": 1100, "type": "state_border"},
            {"name": "West Bengal Border", "km": 1400, "type": "state_border"},
        ],
    },
    "Chennai-Bangalore": {
        "distance_km": 350,
        "duration_hours": 6,
        "highways": ["NH48"],
        "tolls": [
            {"name": "Sriperumbudur Toll", "cost": 80, "km": 40},
            {"name": "Vellore Toll", "cost": 95, "km": 130},
            {"name": "Hosur Toll", "cost": 110, "km": 300},
        ],
        "fuel_stops": [
            {"name": "HP Vellore", "km": 130, "brand": "HP"},
            {"name": "IOCL Hosur", "km": 300, "brand": "Indian Oil"},
        ],
        "checkpoints": [
            {"name": "Tamil Nadu-Karnataka Border", "km": 280, "type": "state_border"},
        ],
    },
    "Ahmedabad-Mumbai": {
        "distance_km": 530,
        "duration_hours": 9,
        "highways": ["NH48"],
        "tolls": [
            {"name": "Vadodara Toll", "cost": 105, "km": 110},
            {"name": "Bharuch Toll", "cost": 95, "km": 200},
            {"name": "Surat Toll", "cost": 135, "km": 290},
            {"name": "Vapi Toll", "cost": 110, "km": 400},
            {"name": "Mumbai Entry", "cost": 180, "km": 520},
        ],
        "fuel_stops": [
            {"name": "IOCL Vadodara", "km": 110, "brand": "Indian Oil"},
            {"name": "Shell Surat", "km": 290, "brand": "Shell"},
            {"name": "BP Vapi", "km": 400, "brand": "BP"},
        ],
        "checkpoints": [
            {"name": "Gujarat-Maharashtra Border", "km": 420, "type": "state_border"},
        ],
    },
    "Pune-Hyderabad": {
        "distance_km": 560,
        "duration_hours": 10,
        "highways": ["NH65"],
        "tolls": [
            {"name": "Solapur Toll", "cost": 120, "km": 250},
            {"name": "Gulbarga Toll", "cost": 105, "km": 380},
            {"name": "Hyderabad Entry", "cost": 150, "km": 550},
        ],
        "fuel_stops": [
            {"name": "IOCL Solapur", "km": 250, "brand": "Indian Oil"},
            {"name": "HP Gulbarga", "km": 380, "brand": "HP"},
        ],
        "checkpoints": [
            {"name": "Maharashtra-Karnataka Border", "km": 300, "type": "state_border"},
            {"name": "Karnataka-Telangana Border", "km": 450, "type": "state_border"},
        ],
    },
}


class MockMapsService:
    """
    Mock maps service providing route and fare calculations for Indian cities.
    """
    
    def __init__(self):
        self.cities = CITY_COORDINATES
        self.routes = PREDEFINED_ROUTES
    
    def get_supported_cities(self) -> List[str]:
        """Get list of all supported cities."""
        return sorted(list(self.cities.keys()))
    
    def get_supported_routes(self) -> List[str]:
        """Get list of pre-defined routes."""
        return list(self.routes.keys())
    
    def get_city_location(self, city: str) -> GeoPoint:
        """Get coordinates for a city."""
        # Try exact match first
        if city in self.cities:
            lat, lng = self.cities[city]
            return GeoPoint(latitude=lat, longitude=lng)
        
        # Try case-insensitive match
        city_lower = city.lower()
        for name, coords in self.cities.items():
            if name.lower() == city_lower:
                return GeoPoint(latitude=coords[0], longitude=coords[1])
        
        raise ValueError(f"City '{city}' not found. Use /maps/cities for supported cities.")
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula."""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + \
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def _generate_polyline(self, origin: GeoPoint, destination: GeoPoint, num_points: int = 10) -> List[Dict[str, float]]:
        """Generate simple polyline between two points."""
        points = []
        for i in range(num_points + 1):
            t = i / num_points
            lat = origin.latitude + t * (destination.latitude - origin.latitude)
            lng = origin.longitude + t * (destination.longitude - origin.longitude)
            points.append({"lat": lat, "lng": lng})
        return points
    
    def _estimate_tolls(self, distance_km: float) -> List[Dict[str, Any]]:
        """Estimate toll costs for a route without predefined data."""
        # Approximate 1 toll every 80-100 km
        num_tolls = max(1, int(distance_km / 90))
        tolls = []
        
        for i in range(num_tolls):
            km = int((i + 1) * distance_km / (num_tolls + 1))
            cost = 80 + (i % 3) * 30  # Vary cost between 80-140
            tolls.append({
                "name": f"Toll Plaza {i + 1}",
                "cost": cost,
                "km": km,
            })
        
        return tolls
    
    def _estimate_fuel_stops(self, distance_km: float) -> List[Dict[str, Any]]:
        """Estimate fuel stops for a route."""
        # Fuel stop every 250-300 km
        num_stops = max(1, int(distance_km / 275))
        brands = ["HP", "Indian Oil", "BP", "Shell", "Reliance"]
        stops = []
        
        for i in range(num_stops):
            km = int((i + 1) * distance_km / (num_stops + 1))
            stops.append({
                "name": f"{brands[i % len(brands)]} Fuel Stop",
                "km": km,
                "brand": brands[i % len(brands)],
            })
        
        return stops
    
    def get_route(self, origin: str, destination: str) -> RouteInfo:
        """
        Get route between two cities.
        
        Uses predefined data if available, otherwise estimates.
        """
        # Get city locations
        origin_point = self.get_city_location(origin)
        dest_point = self.get_city_location(destination)
        
        # Check for predefined route
        route_key = f"{origin}-{destination}"
        reverse_key = f"{destination}-{origin}"
        
        if route_key in self.routes:
            route_data = self.routes[route_key]
            is_estimated = False
        elif reverse_key in self.routes:
            route_data = self.routes[reverse_key]
            is_estimated = False
        else:
            # Estimate route based on straight-line distance * 1.3 (road factor)
            straight_distance = self._haversine_distance(
                origin_point.latitude, origin_point.longitude,
                dest_point.latitude, dest_point.longitude
            )
            distance_km = straight_distance * 1.3
            duration_hours = distance_km / 60  # Assume 60 km/h average
            
            route_data = {
                "distance_km": round(distance_km, 1),
                "duration_hours": round(duration_hours, 1),
                "highways": ["Estimated Route"],
                "tolls": self._estimate_tolls(distance_km),
                "fuel_stops": self._estimate_fuel_stops(distance_km),
                "checkpoints": [],
            }
            is_estimated = True
        
        # Add location data to tolls, fuel stops, checkpoints
        tolls = []
        for toll in route_data["tolls"]:
            t = toll.copy()
            # Interpolate location along route
            progress = toll["km"] / route_data["distance_km"]
            t["location"] = GeoPoint(
                latitude=origin_point.latitude + progress * (dest_point.latitude - origin_point.latitude),
                longitude=origin_point.longitude + progress * (dest_point.longitude - origin_point.longitude),
            )
            tolls.append(t)
        
        fuel_stops = []
        for stop in route_data["fuel_stops"]:
            s = stop.copy()
            progress = stop["km"] / route_data["distance_km"]
            s["location"] = GeoPoint(
                latitude=origin_point.latitude + progress * (dest_point.latitude - origin_point.latitude),
                longitude=origin_point.longitude + progress * (dest_point.longitude - origin_point.longitude),
            )
            fuel_stops.append(s)
        
        checkpoints = []
        for cp in route_data.get("checkpoints", []):
            c = cp.copy()
            progress = cp["km"] / route_data["distance_km"]
            c["location"] = GeoPoint(
                latitude=origin_point.latitude + progress * (dest_point.latitude - origin_point.latitude),
                longitude=origin_point.longitude + progress * (dest_point.longitude - origin_point.longitude),
            )
            checkpoints.append(c)
        
        return RouteInfo(
            origin=origin,
            destination=destination,
            distance_km=route_data["distance_km"],
            duration_hours=route_data["duration_hours"],
            polyline=self._generate_polyline(origin_point, dest_point, 20),
            tolls=tolls,
            fuel_stops=fuel_stops,
            checkpoints=checkpoints,
            highways=route_data["highways"],
            is_estimated=is_estimated,
        )
    
    def calculate_fare(
        self,
        distance_km: float,
        weight_tons: float,
        vehicle_type: str = "hcv",
        toll_cost: float = 0,
    ) -> Dict[str, Any]:
        """
        Calculate freight fare.
        
        Uses Indian trucking industry standard rates.
        """
        # Base rate per km by vehicle type (INR)
        base_rates = {
            "lcv": 18,   # Light Commercial Vehicle
            "hcv": 25,   # Heavy Commercial Vehicle
            "mav": 35,   # Multi-Axle Vehicle
            "trailer": 45,
        }
        
        base_rate = base_rates.get(vehicle_type.lower(), 25)
        
        # Weight factor (increases rate for heavier loads)
        weight_factor = 1.0
        if weight_tons > 10:
            weight_factor = 1.1
        if weight_tons > 20:
            weight_factor = 1.25
        if weight_tons > 30:
            weight_factor = 1.4
        
        # Distance factor (longer routes get slight discount)
        distance_factor = 1.0
        if distance_km > 500:
            distance_factor = 0.95
        if distance_km > 1000:
            distance_factor = 0.9
        
        # Calculate components
        base_fare = distance_km * base_rate * weight_factor * distance_factor
        fuel_surcharge = base_fare * 0.15  # 15% fuel surcharge
        insurance = base_fare * 0.02  # 2% insurance
        
        total = base_fare + fuel_surcharge + insurance + toll_cost
        
        return {
            "base_fare": round(base_fare, 2),
            "fuel_surcharge": round(fuel_surcharge, 2),
            "insurance": round(insurance, 2),
            "toll_cost": round(toll_cost, 2),
            "total": round(total, 2),
            "rate_per_km": round(base_fare / distance_km, 2),
            "rate_per_ton_km": round(base_fare / (distance_km * max(1, weight_tons)), 2),
            "breakdown": {
                "distance_km": distance_km,
                "weight_tons": weight_tons,
                "vehicle_type": vehicle_type,
                "base_rate": base_rate,
                "weight_factor": weight_factor,
                "distance_factor": distance_factor,
            },
        }


# Singleton instance
_maps_service: Optional[MockMapsService] = None


def get_maps_service() -> MockMapsService:
    """Get or create maps service singleton."""
    global _maps_service
    if _maps_service is None:
        _maps_service = MockMapsService()
    return _maps_service
