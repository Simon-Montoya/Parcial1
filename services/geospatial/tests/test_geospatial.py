import pytest
from pathlib import Path

from app.services.geospatial_service import (
    GeospatialService,
    InvalidClusteringParametersError,
)


class FakeRepository:
    def __init__(self, result=None):
        self.result = result
        self.called_with = None

    def get_zone_aggregation(
        self,
        city,
        radius_meters,
        min_points,
    ):
        self.called_with = {
            "city": city,
            "radius_meters": radius_meters,
            "min_points": min_points,
        }

        return self.result


def test_get_zone_success():
    expected = {
        "city": "CALI",
        "radius_meters": 2000,
        "min_points": 3,
        "total_active_emergencies": 5,
        "hotspot_count": 1,
        "hotspots": [
            {
                "cluster_id": 0,
                "emergency_count": 3,
                "center_latitude": 3.4516,
                "center_longitude": -76.532,
                "highest_priority": "P1",
                "emergency_ids": [],
            }
        ],
        "isolated_emergencies": [],
    }

    repository = FakeRepository(result=expected)

    service = GeospatialService(
        repository=repository
    )

    result = service.get_zone(
        city="CALI",
        radius_meters=2000,
        min_points=3,
    )

    assert result == expected
    assert repository.called_with["city"] == "CALI"
    assert repository.called_with["radius_meters"] == 2000
    assert repository.called_with["min_points"] == 3


def test_invalid_radius():
    service = GeospatialService(
        repository=FakeRepository()
    )

    with pytest.raises(
        InvalidClusteringParametersError
    ):
        service.get_zone(
            city="CALI",
            radius_meters=0,
            min_points=3,
        )


def test_invalid_min_points():
    service = GeospatialService(
        repository=FakeRepository()
    )

    with pytest.raises(
        InvalidClusteringParametersError
    ):
        service.get_zone(
            city="CALI",
            radius_meters=2000,
            min_points=1,
        )


def test_zone_migration_excludes_resolved_emergencies():
    migration = (
        Path(__file__).parents[3]
        / "database"
        / "migrations"
        / "004_geospatial_aggregation.sql"
    ).read_text(encoding="utf-8")

    assert "e.status not in" in migration.lower()
    assert "'RESOLVED'" in migration
    assert "'CANCELLED'" in migration
