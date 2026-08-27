from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.models.notification import (
    BroadcastRequest,
    BroadcastResponse,
    WebhookSubscriptionCreate,
    WebhookSubscriptionResponse,
)

from app.services.notification_service import (
    EmergencyNotFoundError,
    NotificationService,
)


router = APIRouter(
    prefix="/notificaciones",
    tags=["notifications"],
)


def get_notification_service():
    return NotificationService()


@router.post(
    "/webhooks",
    response_model=WebhookSubscriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_webhook(
    request: WebhookSubscriptionCreate,
    service: NotificationService = Depends(
        get_notification_service
    ),
):

    return service.create_webhook(
        url=str(request.url),
        event_type=request.event_type,
    )


@router.post(
    "/broadcast",
    response_model=BroadcastResponse,
    status_code=status.HTTP_201_CREATED,
)
def broadcast_notification(
    request: BroadcastRequest,
    service: NotificationService = Depends(
        get_notification_service
    ),
):

    try:

        return service.broadcast(
            emergency_id=request.emergency_id,
            emergency_status=request.status.value,
            message=request.message,
        )

    except EmergencyNotFoundError:

        raise HTTPException(
            status_code=404,
            detail="Emergency not found",
        )