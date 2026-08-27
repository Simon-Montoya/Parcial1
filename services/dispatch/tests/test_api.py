from fastapi.testclient import TestClient

from app.main import app
from app.api.dispatches import get_dispatch_service
from app.services.dispatch_service import NoAvailableUnitError


class FakeDispatchService:
    def assign_unit(self, emergency_id):
        return {
            "dispatch_id": "22222222-2222-2222-2222-222222222222",
            "emergency_id": str(emergency_id),
            "response_unit_id": "33333333-3333-3333-3333-333333333333",
            "response_unit_name": "Bomberos Cali Centro",
            "distance_meters": 350.5,
        }


class FakeNoUnitService:
    def assign_unit(self, emergency_id):
        raise NoAvailableUnitError()


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "dispatch"


def test_assign_dispatch():
    app.dependency_overrides[get_dispatch_service] = (
        lambda: FakeDispatchService()
    )

    response = client.post(
        "/v1/despachos/asignar",
        json={
            "emergency_id":
                "11111111-1111-1111-1111-111111111111"
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["response_unit_name"] == (
        "Bomberos Cali Centro"
    )


def test_invalid_uuid():
    app.dependency_overrides[get_dispatch_service] = (
        lambda: FakeDispatchService()
    )

    response = client.post(
        "/v1/despachos/asignar",
        json={
            "emergency_id": "esto-no-es-un-uuid"
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 422


def test_no_available_unit_returns_409():
    app.dependency_overrides[get_dispatch_service] = (
        lambda: FakeNoUnitService()
    )

    response = client.post(
        "/v1/despachos/asignar",
        json={
            "emergency_id":
                "11111111-1111-1111-1111-111111111111"
        },
    )

    app.dependency_overrides.clear()

    assert response.status_code == 409