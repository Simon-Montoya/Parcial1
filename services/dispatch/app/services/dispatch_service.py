from uuid import UUID

from app.repositories.dispatch_repository import DispatchRepository


class EmergencyNotFoundError(Exception):
    pass


class EmergencyNotAssignableError(Exception):
    pass


class NoAvailableUnitError(Exception):
    pass


class DispatchNotFoundError(Exception):
    pass


class InvalidDispatchTransitionError(Exception):
    pass


class NoActiveDispatchError(Exception):
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

    def update_status(self, dispatch_id: UUID, status: str) -> dict:
        try:
            return self.repository.update_status(dispatch_id, status)
        except Exception as exc:
            message = str(exc)

            if "DISPATCH_NOT_FOUND" in message:
                raise DispatchNotFoundError() from exc

            if any(code in message for code in (
                "INVALID_TARGET_STATUS",
                "INVALID_STATUS_TRANSITION",
                "ALREADY_RESOLVED",
            )):
                raise InvalidDispatchTransitionError() from exc

            raise

    def get_active_dispatch(self, emergency_id: UUID) -> dict:
        dispatch = self.repository.find_active_by_emergency(emergency_id)
        if dispatch is None:
            raise NoActiveDispatchError()
        return dispatch
