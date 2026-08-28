import logging

from fastapi import APIRouter, Depends, HTTPException

from app.models.emergency import EmergencyCreate
from app.services.emergency_service import EmergencyService


router = APIRouter()

logger = logging.getLogger(__name__)


def get_emergency_service() -> EmergencyService:
    """
    Dependency factory.

    El servicio se crea únicamente cuando el endpoint lo necesita.
    Esto evita conectarse a Supabase durante el import de FastAPI
    y facilita los tests mediante dependency overrides.
    """
    return EmergencyService()


@router.post("/emergencias", status_code=201)
def create_emergency(
    emergency: EmergencyCreate,
    service: EmergencyService = Depends(get_emergency_service),
):
    try:
        logger.info(
            "Emergency request received",
            extra={
                "event": "emergency_received",
                "emergency_type": emergency.type.value,
                "city": emergency.city.value,
            },
        )

        created = service.create(emergency)

        logger.info(
            "Emergency created successfully",
            extra={
                "event": "emergency_created",
                "emergency_id": created["id"],
                "emergency_type": created["type"],
                "priority": created["priority"],
                "city": created["city"],
            },
        )

        return {
            "id": created["id"],
            "type": created["type"],
            "city": created["city"],
            "priority": created["priority"],
            "status": created["status"],
            "created_at": created["created_at"],
        }

    except Exception as exc:
        logger.exception(
            "Emergency creation failed",
            extra={
                "event": "emergency_creation_failed",
                "emergency_type": emergency.type.value,
                "city": emergency.city.value,
            },
        )

        raise HTTPException(
            status_code=500,
            detail="Emergency could not be created",
        ) from exc
