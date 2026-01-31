from sqlalchemy import Column, String, Float, Integer, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geography
import enum

from app.db.base import Base


class MissionStatus(str, enum.Enum):
    """Mission lifecycle status."""
    DRAFT = "draft"
    PLANNED = "planned"
    ASSIGNED = "assigned"
    EN_ROUTE_PICKUP = "en_route_pickup"
    AT_PICKUP = "at_pickup"
    LOADING = "loading"
    IN_TRANSIT = "in_transit"
    AT_DELIVERY = "at_delivery"
    UNLOADING = "unloading"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    """Payment status."""
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    REFUNDED = "refunded"


class WaypointType(str, enum.Enum):
    """Type of waypoint stop."""
    ORIGIN = "origin"
    PICKUP = "pickup"
    DROP = "drop"
    FUEL = "fuel"
    REST = "rest"
    CHECKPOINT = "checkpoint"
    DESTINATION = "destination"


class Mission(Base):
    """
    Mission model - central entity for trips.
    
    Connects:
    - Operator (fleet owner)
    - Driver (person driving)
    - Vehicle (truck assigned)
    - Loads (cargo)
    - Waypoints (stops)
    - Agent Decisions (AI decisions)
    """
    
    # Human-readable ID
    mission_number = Column(String(20), unique=True, nullable=False, index=True)
    
    # Participants
    operator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True, index=True)
    
    # Status
    status = Column(Enum(MissionStatus), default=MissionStatus.DRAFT, nullable=False, index=True)
    
    # Origin - PostGIS
    origin = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    origin_address = Column(String(500), nullable=False)
    origin_city = Column(String(100), nullable=True)
    
    # Destination - PostGIS
    destination = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    destination_address = Column(String(500), nullable=False)
    destination_city = Column(String(100), nullable=True)
    
    # Current location (updated during transit)
    current_location = Column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    
    # Route data (from Google Maps)
    route_data = Column(JSONB, default=lambda: {
        "polyline": "",
        "distance_km": 0,
        "duration_minutes": 0,
        "steps": [],
    })
    
    # Timestamps
    planned_start = Column(String(30), nullable=True)
    actual_start = Column(String(30), nullable=True)
    estimated_end = Column(String(30), nullable=True)
    actual_end = Column(String(30), nullable=True)
    
    # Fare - Module 1 output
    quoted_fare = Column(JSONB, default=lambda: {
        "base": 0,
        "distance_charge": 0,
        "fuel_surcharge": 0,
        "toll_charges": 0,
        "loading_charges": 0,
        "difficulty_premium": 0,
        "total": 0,
        "currency": "INR",
    })
    
    actual_fare = Column(JSONB, nullable=True)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Risk Assessment - Module 1 output
    risk_assessment = Column(JSONB, default=lambda: {
        "overall_score": 0,
        "factors": [],
        "eta_range": {
            "optimistic": "",
            "realistic": "",
            "pessimistic": "",
        },
    })
    
    # Agent configuration for this mission
    agent_config = Column(JSONB, default=lambda: {
        "enabled": True,
        "max_detour_km": 30,
        "max_detour_minutes": 45,
        "auto_accept_threshold": 0.8,
    })
    
    # Load details
    cargo_type = Column(String(50), nullable=True)
    cargo_description = Column(Text, nullable=True)
    weight_tons = Column(Float, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Relationships
    operator = relationship("User", back_populates="operated_missions", foreign_keys=[operator_id])
    driver = relationship("User", back_populates="driven_missions", foreign_keys=[driver_id])
    vehicle = relationship("Vehicle", back_populates="missions", foreign_keys=[vehicle_id])
    waypoints = relationship("Waypoint", back_populates="mission", order_by="Waypoint.sequence")
    loads = relationship("MissionLoad", back_populates="mission")
    decisions = relationship("AgentDecision", back_populates="mission", order_by="desc(AgentDecision.created_at)")
    
    # Properties
    @property
    def is_active(self) -> bool:
        return self.status in [
            MissionStatus.EN_ROUTE_PICKUP,
            MissionStatus.AT_PICKUP,
            MissionStatus.LOADING,
            MissionStatus.IN_TRANSIT,
            MissionStatus.AT_DELIVERY,
            MissionStatus.UNLOADING,
        ]
    
    @property
    def is_completed(self) -> bool:
        return self.status == MissionStatus.COMPLETED
    
    @property
    def distance_km(self) -> float:
        return self.route_data.get("distance_km", 0) if self.route_data else 0
    
    @property
    def total_fare(self) -> float:
        return self.quoted_fare.get("total", 0) if self.quoted_fare else 0


class Waypoint(Base):
    """Waypoint stops along mission route."""
    
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False)
    
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    address = Column(String(500), nullable=True)
    
    waypoint_type = Column(Enum(WaypointType), nullable=False)
    
    # Timing
    eta = Column(String(30), nullable=True)
    actual_arrival = Column(String(30), nullable=True)
    actual_departure = Column(String(30), nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    checkpoint_name = Column(String(100), nullable=True)
    estimated_delay_minutes = Column(Float, nullable=True)
    
    mission = relationship("Mission", back_populates="waypoints")
