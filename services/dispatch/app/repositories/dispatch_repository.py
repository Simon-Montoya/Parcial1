import logging
from uuid import UUID

from app.config.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


class DispatchRepository:

    def __init__(self):
        self.supabase = get_supabase_client()

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