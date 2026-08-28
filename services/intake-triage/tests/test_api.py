from fastapi.testclient import TestClient

from app.api.emergencies import get_emergency_service
from app.main import app
from app.services.emergency_service import EmergencyService


client = TestClient(app)


class RecordingRepository:
    def __init__(self):
        self.calls = []

    def create_emergency(self, emergency, priority):
        self.calls.append((emergency, priority))
        return {
            "id": "11111111-1111-1111-1111-111111111111",
            "type": emergency.type.value,
            "city": emergency.city.value,
            "priority": priority,
            "status": "RECEIVED",
            "created_at": "2026-08-27T00:00:00+00:00",
        }


recording_repository = RecordingRepository()


def override_emergency_service():
    return EmergencyService(repository=recording_repository)


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


def test_create_shelter_with_frontend_contract():
    response = client.post("/v1/emergencias", json={
        "type": "SHELTER",
        "city": "PEREIRA",
        "description": "Family needs temporary shelter",
        "latitude": 4.8133,
        "longitude": -75.6961,
        "adults": 2,
        "children": 1,
        "elderly": 1,
        "accessibility_required": True,
        "house_habitable": False,
    })

    assert response.status_code == 201
    assert response.json()["priority"] == "P2"
    assert recording_repository.calls[-1][0].adults == 2


def test_create_supply_with_frontend_contract():
    response = client.post("/v1/emergencias", json={
        "type": "SUPPLY",
        "city": "MANIZALES",
        "description": "Drinking water required",
        "latitude": 5.0703,
        "longitude": -75.5138,
        "supply_category": "WATER",
        "quantity": 20,
        "notes": "Twenty sealed containers",
    })

    assert response.status_code == 201
    assert response.json()["priority"] == "P3"
    assert recording_repository.calls[-1][0].supply_category.value == "WATER"


def test_create_structural_damage_with_frontend_contract():
    response = client.post("/v1/emergencias", json={
        "type": "STRUCTURAL_DAMAGE",
        "city": "CHOCO",
        "description": "Severe wall cracking",
        "latitude": 5.6919,
        "longitude": -76.6583,
        "building_type": "HOUSE",
        "cracking_level": "HIGH",
        "settlement_level": "MEDIUM",
        "collapse_risk": True,
        "road_risk": False,
        "photo_url": "https://example.com/damage.jpg",
    })

    assert response.status_code == 201
    assert response.json()["priority"] == "P4"
    assert recording_repository.calls[-1][0].building_type == "HOUSE"


def test_malformed_structural_damage_returns_422_not_500():
    response = client.post("/v1/emergencias", json={
        "type": "STRUCTURAL_DAMAGE",
        "city": "CALI",
        "description": "Missing required building type",
        "latitude": 3.4516,
        "longitude": -76.532,
        "collapse_risk": True,
    })

    assert response.status_code == 422


def test_unexpected_service_error_is_sanitized():
    class FailingService:
        def create(self, emergency):
            raise AttributeError("sensitive internal detail")

    app.dependency_overrides[get_emergency_service] = lambda: FailingService()
    response = client.post("/v1/emergencias", json={
        "type": "RESCUE",
        "city": "CALI",
        "description": "Test",
        "latitude": 3.4516,
        "longitude": -76.532,
    })
    app.dependency_overrides[get_emergency_service] = override_emergency_service

    assert response.status_code == 500
    assert response.json()["detail"] == "Emergency could not be created"
    assert "sensitive" not in response.text
