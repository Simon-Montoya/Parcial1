from app.models.emergency import EmergencyCreate, Severity
from app.services.triage import TriageService


def test_critical_emergency_is_marked_urgent() -> None:
    emergency = TriageService().process(
        EmergencyCreate(description="Fire reported", severity=Severity.CRITICAL)
    )

    assert emergency.triage_status == "urgent"
