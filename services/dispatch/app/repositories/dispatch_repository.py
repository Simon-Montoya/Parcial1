import logging
from uuid import UUID

from app.config.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


class DispatchRepository:

    def __init__(self, supabase=None):
        self.supabase = (
            supabase if supabase is not None else get_supabase_client()
        )

    def assign_nearest_unit(self, emergency_id: UUID) -> dict:
        logger.info(
            "assigning_nearest_unit",
            extra={
                "emergency_id": str(emergency_id)
            }
        )

        response = (
            self.supabase
            .rpc(
                "assign_nearest_available_unit",
                {
                    "p_emergency_id": str(emergency_id)
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Dispatch assignment returned no data"
            )

        return response.data[0]

    def update_status(self, dispatch_id: UUID, status: str) -> dict:
        logger.info(
            "updating_dispatch_status",
            extra={
                "dispatch_id": str(dispatch_id),
                "target_status": status,
            },
        )

        response = (
            self.supabase
            .rpc(
                "update_dispatch_status",
                {
                    "p_dispatch_id": str(dispatch_id),
                    "p_status": status,
                },
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Dispatch status update returned no data"
            )

        return response.data[0]

    def find_active_by_emergency(self, emergency_id: UUID) -> dict | None:
        response = (
            self.supabase
            .table("dispatches")
            .select(
                "id,emergency_id,response_unit_id,accepted_at,completed_at,"
                "emergencies!inner(status),response_units!inner(name)"
            )
            .eq("emergency_id", str(emergency_id))
            .is_("completed_at", "null")
            .in_("emergencies.status", ["ASSIGNED", "IN_PROGRESS"])
            .order("assigned_at", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            return None

        dispatch = response.data[0]
        return {
            "dispatch_id": dispatch["id"],
            "emergency_id": dispatch["emergency_id"],
            "response_unit_id": dispatch["response_unit_id"],
            "response_unit_name": dispatch["response_units"]["name"],
            "status": dispatch["emergencies"]["status"],
            "accepted_at": dispatch["accepted_at"],
            "completed_at": dispatch["completed_at"],
        }
