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