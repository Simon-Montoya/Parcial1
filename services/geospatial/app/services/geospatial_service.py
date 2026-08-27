from app.repositories.geospatial_repository import (
    GeospatialRepository,
)


class InvalidClusteringParametersError(Exception):
    pass


class GeospatialService:

    def __init__(self, repository=None):
        self.repository = (
            repository
            if repository is not None
            else GeospatialRepository()
        )

    def get_zone(
        self,
        city: str,
        radius_meters: float = 2000,
        min_points: int = 3,
    ) -> dict:

        if radius_meters <= 0:
            raise InvalidClusteringParametersError()

        if min_points < 2:
            raise InvalidClusteringParametersError()

        return self.repository.get_zone_aggregation(
            city=city,
            radius_meters=radius_meters,
            min_points=min_points,
        )