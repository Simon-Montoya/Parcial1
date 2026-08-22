from fastapi import APIRouter, HTTPException

from app.models.emergency import EmergencyCreate
from app.services.emergency_service import EmergencyService


router = APIRouter()

service = EmergencyService()


@router.post("/emergencias", status_code=201)
def create_emergency(emergency: EmergencyCreate):

    try:

        created = service.create(emergency)

        return {
            "id": created["id"],
            "type": created["type"],
            "city": created["city"],
            "priority": created["priority"],
            "status": created["status"],
            "created_at": created["created_at"]
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )