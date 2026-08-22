from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EmergencyType(str, Enum):
    RESCUE = "RESCUE"
    SHELTER = "SHELTER"
    SUPPLY = "SUPPLY"
    STRUCTURAL_DAMAGE = "STRUCTURAL_DAMAGE"


class EmergencyCity(str, Enum):
    CHOCO = "CHOCO"
    PEREIRA = "PEREIRA"
    CALI = "CALI"
    MANIZALES = "MANIZALES"


class EmergencyCreate(BaseModel):
    type: EmergencyType
    city: EmergencyCity

    description: Optional[str] = None

    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)

    trapped_people: int = Field(default=0, ge=0)
    injured_people: int = Field(default=0, ge=0)

    gas_leak: bool = False
    fire: bool = False
    imminent_collapse_risk: bool = False