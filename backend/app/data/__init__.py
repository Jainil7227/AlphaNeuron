"""Data module - Mock data and in-memory storage."""

from app.data.mock_routes import INDIAN_ROUTES, get_route_info
from app.data.mock_loads import AVAILABLE_LOADS, get_available_loads, get_backhaul_loads
from app.data.store import DataStore, get_store

__all__ = [
    "INDIAN_ROUTES",
    "get_route_info",
    "AVAILABLE_LOADS", 
    "get_available_loads",
    "get_backhaul_loads",
    "DataStore",
    "get_store",
]
