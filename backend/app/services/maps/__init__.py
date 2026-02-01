"""
Maps Service Module.

Provides route calculation, distance estimation, and fare calculation
using mock data for Indian cities (no external API required).
"""

from app.services.maps.mock_maps import (
    MockMapsService,
    get_maps_service,
    GeoPoint,
    RouteInfo,
)

__all__ = [
    "MockMapsService",
    "get_maps_service",
    "GeoPoint",
    "RouteInfo",
]
