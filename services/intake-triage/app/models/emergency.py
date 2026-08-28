from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class SupplyCategory(str, Enum):
    WATER = "WATER"
    FOOD = "FOOD"
    FIRST_AID = "FIRST_AID"
    CHRONIC_MEDICATION = "CHRONIC_MEDICATION"


class EmergencyCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

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

    adults: int = Field(default=0, ge=0)
    children: int = Field(default=0, ge=0)
    elderly: int = Field(default=0, ge=0)
    accessibility_required: bool = False
    house_habitable: Optional[bool] = None

    supply_category: Optional[SupplyCategory] = None
    quantity: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None

    building_type: Optional[str] = None
    cracking_level: Optional[str] = None
    settlement_level: Optional[str] = None
    collapse_risk: bool = False
    road_risk: bool = False
    photo_url: Optional[str] = None

    @model_validator(mode="after")
    def validate_specialized_fields(self):
        if (
            self.type == EmergencyType.SUPPLY
            and self.supply_category is None
        ):
            raise ValueError(
                "supply_category is required for SUPPLY emergencies"
            )

        if (
            self.type == EmergencyType.STRUCTURAL_DAMAGE
            and not (self.building_type or "").strip()
        ):
            raise ValueError(
                "building_type is required for STRUCTURAL_DAMAGE emergencies"
            )

        return self
