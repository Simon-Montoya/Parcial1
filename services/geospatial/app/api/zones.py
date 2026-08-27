from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.models.zone import (
    EmergencyCity,
    ZoneAggregationResponse,
)
from app.services.geospatial_service import (
    GeospatialService,
    InvalidClusteringParametersError,
)


router = APIRouter(
    prefix="/emergencias/zona",
    tags=["geospatial"],
)


def get_geospatial_service():
    return GeospatialService()


@router.get(
    "/{city}",
    response_model=ZoneAggregationResponse,
)
def get_zone_aggregation(
    city: EmergencyCity,
    radius_meters: float = Query(
        default=2000,
        gt=0,
        le=20000,
    ),
    min_points: int = Query(
        default=3,
        ge=2,
        le=20,
    ),
    service: GeospatialService = Depends(
        get_geospatial_service
    ),
):
    try:
        return service.get_zone(
            city=city.value,
            radius_meters=radius_meters,
            min_points=min_points,
        )

    except InvalidClusteringParametersError:
        raise HTTPException(
            status_code=400,
            detail="Invalid clustering parameters",
        )