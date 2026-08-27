import logging

from app.config.supabase_client import get_supabase_client


logger = logging.getLogger(__name__)


class GeospatialRepository:

    def __init__(self):
        self.supabase = get_supabase_client()

    def get_zone_aggregation(
        self,
        city: str,
        radius_meters: float,
        min_points: int,
    ) -> dict:

        logger.info(
            "zone_aggregation_requested",
            extra={
                "city": city,
                "radius_meters": radius_meters,
                "min_points": min_points,
            },
        )

        response = (
            self.supabase
            .rpc(
                "get_zone_aggregation",
                {
                    "p_city": city,
                    "p_radius_meters": radius_meters,
                    "p_min_points": min_points,
                },
            )
            .execute()
        )

        if response.data is None:
            raise RuntimeError(
                "Zone aggregation returned no data"
            )

        return response.data