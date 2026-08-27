import pytest
from pydantic import ValidationError

from app.models.emergency import EmergencyCreate


def valid_rescue_payload():
    return {
        "type": "RESCUE",
        "city": "CALI",
        "description": "Test emergency",
        "latitude": 3.4516,
        "longitude": -76.532,
        "trapped_people": 2,
        "injured_people": 1,
        "gas_leak": False,
        "fire": False,
        "imminent_collapse_risk": False,
    }


def test_invalid_latitude():
    payload = valid_rescue_payload()
    payload["latitude"] = 120

    with pytest.raises(ValidationError):
        EmergencyCreate(**payload)


def test_invalid_longitude():
    payload = valid_rescue_payload()
    payload["longitude"] = -200

    with pytest.raises(ValidationError):
        EmergencyCreate(**payload)


def test_invalid_city():
    payload = valid_rescue_payload()
    payload["city"] = "BOGOTA"

    with pytest.raises(ValidationError):
        EmergencyCreate(**payload)


def test_invalid_type():
    payload = valid_rescue_payload()
    payload["type"] = "OTHER"

    with pytest.raises(ValidationError):
        EmergencyCreate(**payload)


def test_negative_trapped_people():
    payload = valid_rescue_payload()
    payload["trapped_people"] = -1

    with pytest.raises(ValidationError):
        EmergencyCreate(**payload)