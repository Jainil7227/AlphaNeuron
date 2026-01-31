from sqlalchemy import Column, String, Float, Enum, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geography
import enum

from app.db.base import Base


class CheckpointType(str, enum.Enum):
    """Type of infrastructure checkpoint."""
    TOLL_PLAZA = "toll_plaza"
    RTO_CHECKPOINT = "rto_checkpoint"
    BORDER_CHECKPOINT = "border_checkpoint"
    WEIGH_BRIDGE = "weigh_bridge"
    OCTROI_POST = "octroi_post"
    POLICE_CHECKPOINT = "police_checkpoint"
    PERMIT_CHECK = "permit_check"


class Checkpoint(Base):
    """
    Infrastructure checkpoint model.
    
    Module 1: Context-Aware Mission Planner
    - Toll plazas with vehicle-wise charges
    - Checkposts with average delays
    - No-entry timing restrictions
    - Operating hours
    """
    
    # Identification
    name = Column(String(200), nullable=False)
    code = Column(String(50), unique=True, nullable=True, index=True)
    checkpoint_type = Column(Enum(CheckpointType), nullable=False, index=True)
    
    # Location - PostGIS
    location = Column(Geography(geometry_type="POINT", srid=4326), nullable=False)
    
    # Address
    highway_name = Column(String(100), nullable=True)
    state = Column(String(50), nullable=False, index=True)
    district = Column(String(100), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Toll Charges (vehicle type -> charge in INR)
    toll_charges = Column(JSONB, default=lambda: {
        "mini_truck": 0,
        "lcv": 0,
        "icv": 0,
        "mcv": 0,
        "hcv": 0,
        "mav": 0,
        "trailer": 0,
        "container": 0,
    })
    
    # FASTag accepted
    fastag_enabled = Column(Boolean, default=True)
    
    # Average delays in minutes (by time of day)
    avg_delays = Column(JSONB, default=lambda: {
        "morning": 10,
        "day": 5,
        "evening": 15,
        "night": 5,
    })
    
    # Operating hours
    operating_hours = Column(JSONB, default=lambda: {
        "open_24x7": True,
        "open_time": "00:00",
        "close_time": "23:59",
    })
    
    # No-entry timings for trucks
    no_entry_timings = Column(JSONB, default=lambda: {
        "enabled": False,
        "restricted_start": "",
        "restricted_end": "",
        "vehicle_types": [],
        "notes": "",
    })
    
    # Additional info
    amenities = Column(JSONB, default=lambda: {
        "fuel_station": False,
        "rest_area": False,
        "food_court": False,
        "parking": False,
        "repair_shop": False,
    })
    
    # Contact
    contact_number = Column(String(15), nullable=True)
    
    # Properties
    @property
    def is_toll(self) -> bool:
        return self.checkpoint_type == CheckpointType.TOLL_PLAZA
    
    @property
    def has_no_entry(self) -> bool:
        return self.no_entry_timings.get("enabled", False) if self.no_entry_timings else False
    
    def get_toll_for_vehicle(self, vehicle_type: str) -> float:
        """Get toll charge for specific vehicle type."""
        if not self.toll_charges:
            return 0
        return self.toll_charges.get(vehicle_type.lower(), 0)
    
    def get_avg_delay(self, time_of_day: str = "day") -> int:
        """Get average delay for time of day."""
        if not self.avg_delays:
            return 10
        return self.avg_delays.get(time_of_day, 10)
    
    def is_open_at(self, hour: int) -> bool:
        """Check if checkpoint is open at given hour (0-23)."""
        if not self.operating_hours:
            return True
        if self.operating_hours.get("open_24x7", True):
            return True
        open_time = int(self.operating_hours.get("open_time", "00:00").split(":")[0])
        close_time = int(self.operating_hours.get("close_time", "23:59").split(":")[0])
        return open_time <= hour <= close_time
