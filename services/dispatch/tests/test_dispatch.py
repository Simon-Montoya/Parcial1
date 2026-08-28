from uuid import UUID
from pathlib import Path

import pytest

from app.services.dispatch_service import (
    DispatchService,
    EmergencyNotFoundError,
    EmergencyNotAssignableError,
    NoAvailableUnitError,
    DispatchNotFoundError,
    InvalidDispatchTransitionError,
)


EMERGENCY_ID = UUID("11111111-1111-1111-1111-111111111111")


class FakeRepository:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    def assign_nearest_unit(self, emergency_id):
        if self.error:
            raise self.error
        return self.result

    def update_status(self, dispatch_id, status):
        if self.error:
            raise self.error
        return self.result


def test_assign_unit_success():
    expected = {
        "dispatch_id": "22222222-2222-2222-2222-222222222222",
        "emergency_id": str(EMERGENCY_ID),
        "response_unit_id": "33333333-3333-3333-3333-333333333333",
        "response_unit_name": "Bomberos Cali Centro",
        "distance_meters": 350.5,
    }

    service = DispatchService(
        repository=FakeRepository(result=expected)
    )

    result = service.assign_unit(EMERGENCY_ID)

    assert result == expected


def test_emergency_not_found():
    service = DispatchService(
        repository=FakeRepository(
            error=RuntimeError("EMERGENCY_NOT_FOUND")
        )
    )

    with pytest.raises(EmergencyNotFoundError):
        service.assign_unit(EMERGENCY_ID)


def test_emergency_not_assignable():
    service = DispatchService(
        repository=FakeRepository(
            error=RuntimeError("EMERGENCY_NOT_ASSIGNABLE")
        )
    )

    with pytest.raises(EmergencyNotAssignableError):
        service.assign_unit(EMERGENCY_ID)


def test_no_available_unit():
    service = DispatchService(
        repository=FakeRepository(
            error=RuntimeError("NO_AVAILABLE_UNIT")
        )
    )

    with pytest.raises(NoAvailableUnitError):
        service.assign_unit(EMERGENCY_ID)


DISPATCH_ID = UUID("22222222-2222-2222-2222-222222222222")


def test_resolve_assigned_dispatch():
    expected = {
        "dispatch_id": str(DISPATCH_ID),
        "emergency_id": str(EMERGENCY_ID),
        "response_unit_id": "33333333-3333-3333-3333-333333333333",
        "response_unit_name": "Bomberos Cali Centro",
        "status": "RESOLVED",
        "completed_at": "2026-08-28T12:00:00+00:00",
    }
    service = DispatchService(FakeRepository(result=expected))

    assert service.update_status(DISPATCH_ID, "RESOLVED") == expected


def test_dispatch_not_found_when_updating_status():
    service = DispatchService(FakeRepository(
        error=RuntimeError("DISPATCH_NOT_FOUND")
    ))

    with pytest.raises(DispatchNotFoundError):
        service.update_status(DISPATCH_ID, "RESOLVED")


@pytest.mark.parametrize("database_error", [
    "INVALID_STATUS_TRANSITION",
    "ALREADY_RESOLVED",
    "INVALID_TARGET_STATUS",
])
def test_invalid_or_repeated_transition(database_error):
    service = DispatchService(FakeRepository(
        error=RuntimeError(database_error)
    ))

    with pytest.raises(InvalidDispatchTransitionError):
        service.update_status(DISPATCH_ID, "RESOLVED")


def test_unexpected_update_error_is_not_hidden():
    service = DispatchService(FakeRepository(
        error=RuntimeError("DATABASE_UNAVAILABLE")
    ))

    with pytest.raises(RuntimeError, match="DATABASE_UNAVAILABLE"):
        service.update_status(DISPATCH_ID, "RESOLVED")


def test_lifecycle_migration_keeps_resolution_atomic_and_auditable():
    migration = (
        Path(__file__).parents[3]
        / "database"
        / "migrations"
        / "005_dispatch_lifecycle.sql"
    ).read_text(encoding="utf-8")

    assert "for update of d, e" in migration.lower()
    assert "set status = 'RESOLVED'" not in migration
    assert "set status = p_status" in migration
    assert "set status = 'AVAILABLE'" in migration
    assert "insert into emergency_status_history" in migration
    assert "delete from" not in migration.lower()
