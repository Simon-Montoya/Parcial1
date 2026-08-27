from app.models.emergency import (
    EmergencyCreate,
    EmergencyType,
    EmergencyCity,
)

from app.services.triage import calculate_priority


def create_emergency(emergency_type: EmergencyType) -> EmergencyCreate:
    """
    Construye una emergencia mínima para probar exclusivamente
    la lógica determinística de triage.

    model_construct evita que los campos específicos de P1/P2/P3/P4
    interfieran con este unit test.
    """
    return EmergencyCreate.model_construct(
        type=emergency_type,
        city=EmergencyCity.CALI,
        description="Emergency used for triage testing",
        latitude=3.4516,
        longitude=-76.5320,
    )


def test_rescue_priority():
    emergency = create_emergency(EmergencyType.RESCUE)

    assert calculate_priority(emergency) == "P1"


def test_shelter_priority():
    emergency = create_emergency(EmergencyType.SHELTER)

    assert calculate_priority(emergency) == "P2"


def test_supply_priority():
    emergency = create_emergency(EmergencyType.SUPPLY)

    assert calculate_priority(emergency) == "P3"


def test_structural_damage_priority():
    emergency = create_emergency(
        EmergencyType.STRUCTURAL_DAMAGE
    )

    assert calculate_priority(emergency) == "P4"