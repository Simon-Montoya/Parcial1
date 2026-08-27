from fastapi.testclient import TestClient

from app.api.emergencies import get_emergency_service
from app.main import app


client = TestClient(app)


class FakeEmergencyService:

    def create(self, emergency):
        return {
            "id": "11111111-1111-1111-1111-111111111111",
            "type": emergency.type.value,
            "city": emergency.city.value,
            "priority": "P1",
            "status": "RECEIVED",
            "created_at": "2026-08-27T00:00:00+00:00",
        }


def override_emergency_service():
    return FakeEmergencyService()


app.dependency_overrides[
    get_emergency_service
] = override_emergency_service


def test_health_check():

    response = client.get("/health")

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "service": "intake-triage",
        "version": "1.0.0",
    }


def test_create_rescue_emergency():

    payload = {
        "type": "RESCUE",
        "city": "CALI",
        "description": "Collapsed building",
        "latitude": 3.4516,
        "longitude": -76.532,
        "trapped_people": 3,
        "injured_people": 1,
        "gas_leak": True,
        "fire": False,
        "imminent_collapse_risk": True,
    }

    response = client.post(
        "/v1/emergencias",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["type"] == "RESCUE"
    assert body["priority"] == "P1"
    assert body["city"] == "CALI"
    assert body["status"] == "RECEIVED"


def test_invalid_city_returns_422():

    payload = {
        "type": "RESCUE",
        "city": "BOGOTA",
        "description": "Invalid city test",
        "latitude": 4.711,
        "longitude": -74.0721,
        "trapped_people": 1,
        "injured_people": 0,
        "gas_leak": False,
        "fire": False,
        "imminent_collapse_risk": False,
    }

    response = client.post(
        "/v1/emergencias",
        json=payload,
    )

    assert response.status_code == 422


def test_invalid_coordinates_returns_422():

    payload = {
        "type": "RESCUE",
        "city": "CALI",
        "description": "Invalid coordinates",
        "latitude": 150,
        "longitude": -76.532,
        "trapped_people": 1,
        "injured_people": 0,
        "gas_leak": False,
        "fire": False,
        "imminent_collapse_risk": False,
    }

    response = client.post(
        "/v1/emergencias",
        json=payload,
    )

    assert response.status_code == 422