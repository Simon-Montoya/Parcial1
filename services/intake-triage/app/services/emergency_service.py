from app.models.emergency import EmergencyCreate
from app.repositories.emergency_repository import EmergencyRepository
from app.services.triage import calculate_priority


class EmergencyService:

    def __init__(self):
        self.repository = EmergencyRepository()

    def create(self, emergency: EmergencyCreate) -> dict:

        priority = calculate_priority(emergency)

        created = self.repository.create_emergency(
            emergency=emergency,
            priority=priority
        )

        return created