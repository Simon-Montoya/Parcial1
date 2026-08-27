from uuid import UUID

import pytest

from app.services.dispatch_service import (
    DispatchService,
    EmergencyNotFoundError,
    EmergencyNotAssignableError,
    NoAvailableUnitError,
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