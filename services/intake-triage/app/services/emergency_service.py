from app.models.emergency import EmergencyCreate
from app.repositories.emergency_repository import (
    EmergencyRepository,
)
from app.services.triage import calculate_priority


class EmergencyService:

    def __init__(
        self,
        repository: EmergencyRepository | None = None,
    ):
        self.repository = (
            repository
            if repository is not None
            else EmergencyRepository()
        )

    def create(
        self,
        emergency: EmergencyCreate,
    ) -> dict:

        priority = calculate_priority(
            emergency
        )

        return self.repository.create_emergency(
            emergency=emergency,
            priority=priority,
        )