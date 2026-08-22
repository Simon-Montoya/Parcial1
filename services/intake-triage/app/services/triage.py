from app.models.emergency import EmergencyCreate, EmergencyType


def calculate_priority(emergency: EmergencyCreate) -> str:

    if emergency.type == EmergencyType.RESCUE:
        return "P1"

    if emergency.type == EmergencyType.SHELTER:
        return "P2"

    if emergency.type == EmergencyType.SUPPLY:
        return "P3"

    if emergency.type == EmergencyType.STRUCTURAL_DAMAGE:
        return "P4"

    raise ValueError("Unsupported emergency type")
