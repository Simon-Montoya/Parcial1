import pytest
from fastapi.testclient import TestClient

from app.api.notifications import (
    get_notification_service,
)
from app.main import app


class FakeNotificationService:
    def broadcast(
        self,
        emergency_id,
        emergency_status,
        message,
    ):
        return {
            "notification_id":
                "22222222-2222-2222-2222-222222222222",
            "emergency_id":
                str(emergency_id),
            "event_type":
                "EMERGENCY_STATUS_CHANGED",
            "status":
                "SENT",
            "webhook_delivered":
                0,
            "webhook_failed":
                0,
        }


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "notifications"


def test_broadcast():
    app.dependency_overrides[
        get_notification_service
    ] = lambda: FakeNotificationService()

    response = client.post(
        "/v1/notificaciones/broadcast",
        json={
            "emergency_id":
                "11111111-1111-1111-1111-111111111111",
            "status":
                "ASSIGNED",
            "message":
                "Unidad asignada",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "SENT"


def test_invalid_uuid():
    app.dependency_overrides[
        get_notification_service
    ] = lambda: FakeNotificationService()

    response = client.post(
        "/v1/notificaciones/broadcast",
        json={
            "emergency_id":
                "uuid-invalido",
            "status":
                "ASSIGNED",
            "message":
                "Test",
        },
    )

    assert response.status_code == 422