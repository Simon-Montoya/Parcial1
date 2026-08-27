# tests/test_notifications.py
from uuid import UUID

import pytest

from app.services.notification_service import (
    EmergencyNotFoundError,
    NotificationService,
)

EMERGENCY_ID = UUID("11111111-1111-1111-1111-111111111111")
NOTIFICATION_ID = "22222222-2222-2222-2222-222222222222"


class FakeRepository:
    def __init__(self, exists=True):
        self.exists = exists
        self.updated_status = None

    def emergency_exists(self, emergency_id):
        return self.exists

    def create_notification(
        self,
        emergency_id,
        message,
        event_type,
        payload,
    ):
        return {"id": NOTIFICATION_ID}

    def get_active_webhooks(self, event_type):
        return []

    def update_notification_status(
        self,
        notification_id,
        status,
    ):
        self.updated_status = status

    def record_delivery(self, **kwargs):
        pass


def test_broadcast_without_webhooks():
    repository = FakeRepository()

    service = NotificationService(
        repository=repository
    )

    result = service.broadcast(
        emergency_id=EMERGENCY_ID,
        emergency_status="ASSIGNED",
        message="Unidad asignada",
    )

    assert result["emergency_id"] == EMERGENCY_ID
    assert result["status"] == "SENT"
    assert result["webhook_delivered"] == 0
    assert result["webhook_failed"] == 0
    assert repository.updated_status == "SENT"


def test_emergency_not_found():
    service = NotificationService(
        repository=FakeRepository(exists=False)
    )

    with pytest.raises(EmergencyNotFoundError):
        service.broadcast(
            emergency_id=EMERGENCY_ID,
            emergency_status="ASSIGNED",
            message="Test",
        )