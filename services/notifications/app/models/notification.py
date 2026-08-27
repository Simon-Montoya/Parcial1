from enum import Enum
from uuid import UUID

from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
)


class EmergencyStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class WebhookSubscriptionCreate(BaseModel):
    url: HttpUrl
    event_type: str = "EMERGENCY_STATUS_CHANGED"


class WebhookSubscriptionResponse(BaseModel):
    id: UUID
    url: str
    event_type: str
    active: bool


class BroadcastRequest(BaseModel):
    emergency_id: UUID
    status: EmergencyStatus

    message: str = Field(
        min_length=1,
        max_length=500,
    )


class BroadcastResponse(BaseModel):
    notification_id: UUID
    emergency_id: UUID
    event_type: str
    status: str
    webhook_delivered: int
    webhook_failed: int