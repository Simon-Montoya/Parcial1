from uuid import UUID

from app.repositories.dispatch_repository import DispatchRepository


class EmergencyNotFoundError(Exception):
    pass


class EmergencyNotAssignableError(Exception):
    pass


class NoAvailableUnitError(Exception):
    pass


class DispatchService:

    def __init__(self, repository=None):
        self.repository = (
            repository
            if repository is not None
            else DispatchRepository()
        )

    def assign_unit(self, emergency_id: UUID) -> dict:
        try:
            return self.repository.assign_nearest_unit(
                emergency_id
            )

        except Exception as exc:
            message = str(exc)

            if "EMERGENCY_NOT_FOUND" in message:
                raise EmergencyNotFoundError() from exc

            if "EMERGENCY_NOT_ASSIGNABLE" in message:
                raise EmergencyNotAssignableError() from exc

            if "NO_AVAILABLE_UNIT" in message:
                raise NoAvailableUnitError() from exc

            raise