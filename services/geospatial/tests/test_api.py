import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.zones import get_geospatial_service


class FakeGeospatialService:

    def get_zone(
        self,
        city,
        radius_meters=2000,
        min_points=3,
    ):
        return {
            "city": city,
            "radius_meters": radius_meters,
            "min_points": min_points,
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


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()

    yield

    app.dependency_overrides.clear()


def override_service():
    app.dependency_overrides[
        get_geospatial_service
    ] = lambda: FakeGeospatialService()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "geospatial"


def test_get_zone():
    override_service()

    response = client.get(
        "/v1/emergencias/zona/CALI"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["city"] == "CALI"
    assert data["hotspot_count"] == 1
    assert data["total_active_emergencies"] == 5


def test_custom_clustering_parameters():
    override_service()

    response = client.get(
        "/v1/emergencias/zona/CALI"
        "?radius_meters=1500&min_points=4"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["radius_meters"] == 1500
    assert data["min_points"] == 4


def test_invalid_city():
    override_service()

    response = client.get(
        "/v1/emergencias/zona/BOGOTA"
    )

    assert response.status_code == 422


def test_invalid_radius():
    override_service()

    response = client.get(
        "/v1/emergencias/zona/CALI"
        "?radius_meters=-100"
    )

    assert response.status_code == 422


def test_invalid_min_points():
    override_service()

    response = client.get(
        "/v1/emergencias/zona/CALI"
        "?min_points=1"
    )

    assert response.status_code == 422