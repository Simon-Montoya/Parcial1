from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EmergencyCity(str, Enum):
    CHOCO = "CHOCO"
    PEREIRA = "PEREIRA"
    CALI = "CALI"
    MANIZALES = "MANIZALES"


class ZoneAggregationResponse(BaseModel):
    city: EmergencyCity
    radius_meters: float
    min_points: int
    total_active_emergencies: int
    hotspot_count: int
    hotspots: list[dict[str, Any]]
    isolated_emergencies: list[dict[str, Any]]