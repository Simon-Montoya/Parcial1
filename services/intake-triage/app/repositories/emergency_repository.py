import logging
from enum import Enum

from app.config.supabase_client import get_supabase_client
from app.models.emergency import (
    EmergencyCreate,
    EmergencyType,
)


logger = logging.getLogger(__name__)


def enum_value(value):
    if isinstance(value, Enum):
        return value.value

    return value


class EmergencyRepository:

    def __init__(self):
        self.supabase = get_supabase_client()

    def create_emergency(
        self,
        emergency: EmergencyCreate,
        priority: str,
    ) -> dict:

        emergency_data = {
            "type": emergency.type.value,
            "priority": priority,
            "status": "RECEIVED",
            "city": emergency.city.value,
            "description": emergency.description,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude,
        }

        response = (
            self.supabase
            .table("emergencies")
            .insert(emergency_data)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Emergency could not be created"
            )

        created_emergency = response.data[0]

        emergency_id = created_emergency["id"]

        try:

            self._create_emergency_details(
                emergency_id=emergency_id,
                emergency=emergency,
            )

        except Exception:
            logger.exception(
                "Emergency detail creation failed",
                extra={
                    "event": "emergency_detail_failed",
                    "emergency_id": emergency_id,
                    "emergency_type": emergency.type.value,
                },
            )

            # Compensating transaction:
            # si el detalle falla, evitamos dejar una emergencia
            # incompleta en la base de datos.
            (
                self.supabase
                .table("emergencies")
                .delete()
                .eq("id", emergency_id)
                .execute()
            )

            raise

        return created_emergency

    def _create_emergency_details(
        self,
        emergency_id: str,
        emergency: EmergencyCreate,
    ) -> None:

        if emergency.type == EmergencyType.RESCUE:

            data = {
                "emergency_id": emergency_id,
                "trapped_people": emergency.trapped_people,
                "injured_people": emergency.injured_people,
                "gas_leak": emergency.gas_leak,
                "fire": emergency.fire,
                "imminent_collapse_risk":
                    emergency.imminent_collapse_risk,
            }

            table = "rescue_details"

        elif emergency.type == EmergencyType.SHELTER:

            data = {
                "emergency_id": emergency_id,
                "adults": emergency.adults,
                "children": emergency.children,
                "elderly": emergency.elderly,
                "accessibility_required":
                    emergency.accessibility_required,
                "house_habitable":
                    emergency.house_habitable,
            }

            table = "shelter_details"

        elif emergency.type == EmergencyType.SUPPLY:

            data = {
                "emergency_id": emergency_id,
                "supply_category":
                    enum_value(emergency.supply_category),
                "quantity": emergency.quantity,
                "notes": emergency.notes,
            }

            table = "supply_details"

        elif emergency.type == EmergencyType.STRUCTURAL_DAMAGE:

            data = {
                "emergency_id": emergency_id,
                "building_type": emergency.building_type,
                "cracking_level": emergency.cracking_level,
                "settlement_level": emergency.settlement_level,
                "collapse_risk": emergency.collapse_risk,
                "road_risk": emergency.road_risk,
                "photo_url": emergency.photo_url,
            }

            table = "structural_damage_details"

        else:
            raise ValueError(
                f"Unsupported emergency type: {emergency.type}"
            )

        response = (
            self.supabase
            .table(table)
            .insert(data)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                f"Emergency details could not be created "
                f"in {table}"
            )

        logger.info(
            "Emergency details created",
            extra={
                "event": "emergency_details_created",
                "emergency_id": emergency_id,
                "details_table": table,
            },
        )