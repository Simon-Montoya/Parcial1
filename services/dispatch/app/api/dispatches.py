from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.dispatch import (
    DispatchAssignRequest,
    DispatchAssignResponse,
    DispatchStatusUpdateRequest,
    DispatchStatusUpdateResponse,
)
from app.services.dispatch_service import (
    DispatchService,
    EmergencyNotAssignableError,
    EmergencyNotFoundError,
    NoAvailableUnitError,
    DispatchNotFoundError,
    InvalidDispatchTransitionError,
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


@router.patch(
    "/{dispatch_id}",
    response_model=DispatchStatusUpdateResponse,
)
def update_dispatch_status(
    dispatch_id: UUID,
    request: DispatchStatusUpdateRequest,
    service: DispatchService = Depends(get_dispatch_service),
):
    try:
        return service.update_status(
            dispatch_id=dispatch_id,
            status=request.status.value,
        )
    except DispatchNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Dispatch not found",
        )
    except InvalidDispatchTransitionError:
        raise HTTPException(
            status_code=409,
            detail="Invalid dispatch status transition",
        )
