from fastapi import APIRouter, Depends, HTTPException, status

from app.models.dispatch import (
    DispatchAssignRequest,
    DispatchAssignResponse,
)
from app.services.dispatch_service import (
    DispatchService,
    EmergencyNotAssignableError,
    EmergencyNotFoundError,
    NoAvailableUnitError,
)


router = APIRouter(
    prefix="/despachos",
    tags=["dispatches"],
)


def get_dispatch_service():
    return DispatchService()


@router.post(
    "/asignar",
    response_model=DispatchAssignResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_dispatch(
    request: DispatchAssignRequest,
    service: DispatchService = Depends(
        get_dispatch_service
    ),
):
    try:
        return service.assign_unit(
            request.emergency_id
        )

    except EmergencyNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Emergency not found",
        )

    except EmergencyNotAssignableError:
        raise HTTPException(
            status_code=409,
            detail="Emergency is not available for assignment",
        )

    except NoAvailableUnitError:
        raise HTTPException(
            status_code=409,
            detail="No available response unit found",
        )