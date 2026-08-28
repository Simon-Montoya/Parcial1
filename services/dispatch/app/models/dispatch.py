from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class DispatchAssignRequest(BaseModel):
    emergency_id: UUID


class DispatchAssignResponse(BaseModel):
    dispatch_id: UUID
    emergency_id: UUID
    response_unit_id: UUID
    response_unit_name: str
    distance_meters: float


class DispatchLifecycleStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"


class ActiveDispatchStatus(str, Enum):
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"


class DispatchStatusUpdateRequest(BaseModel):
    status: DispatchLifecycleStatus


class DispatchStatusUpdateResponse(BaseModel):
    dispatch_id: UUID
    emergency_id: UUID
    response_unit_id: UUID
    response_unit_name: str
    status: DispatchLifecycleStatus
    completed_at: datetime | None = None


class ActiveDispatchResponse(BaseModel):
    dispatch_id: UUID
    emergency_id: UUID
    response_unit_id: UUID
    response_unit_name: str
    status: ActiveDispatchStatus
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
