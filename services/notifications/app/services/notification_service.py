import logging
from uuid import UUID

import httpx

from app.repositories.notification_repository import (
    NotificationRepository,
)


logger = logging.getLogger(__name__)


class EmergencyNotFoundError(Exception):
    pass


class NotificationService:

    EVENT_TYPE = "EMERGENCY_STATUS_CHANGED"

    def __init__(
        self,
        repository=None,
    ):
        self.repository = (
            repository
            if repository is not None
            else NotificationRepository()
        )

    def create_webhook(
        self,
        url: str,
        event_type: str,
    ):
        return self.repository.create_webhook(
            url=url,
            event_type=event_type,
        )

    def broadcast(
        self,
        emergency_id: UUID,
        emergency_status: str,
        message: str,
    ) -> dict:

        if not self.repository.emergency_exists(
            emergency_id
        ):
            raise EmergencyNotFoundError()

        payload = {
            "event":
                self.EVENT_TYPE,

            "emergency_id":
                str(emergency_id),

            "status":
                emergency_status,

            "message":
                message,
        }

        notification = (
            self.repository.create_notification(
                emergency_id=emergency_id,
                message=message,
                event_type=self.EVENT_TYPE,
                payload=payload,
            )
        )

        notification_id = UUID(
            notification["id"]
        )

        subscriptions = (
            self.repository.get_active_webhooks(
                self.EVENT_TYPE
            )
        )

        delivered = 0
        failed = 0

        for subscription in subscriptions:

            http_status = None
            error_message = None
            success = False

            try:

                response = httpx.post(
                    subscription["url"],
                    json=payload,
                    timeout=3.0,
                )

                http_status = (
                    response.status_code
                )

                success = (
                    200
                    <= response.status_code
                    < 300
                )

            except Exception as exc:
                error_message = str(exc)

            if success:
                delivered += 1
            else:
                failed += 1

            self.repository.record_delivery(
                notification_id=notification_id,
                subscription_id=UUID(
                    subscription["id"]
                ),
                http_status=http_status,
                success=success,
                error_message=error_message,
            )

        final_status = (
            "SENT"
            if failed == 0
            else "FAILED"
        )

        self.repository.update_notification_status(
            notification_id,
            final_status,
        )

        logger.info(
            "notification_broadcast_completed",
            extra={
                "notification_id":
                    str(notification_id),
                "delivered":
                    delivered,
                "failed":
                    failed,
            },
        )

        return {
            "notification_id":
                notification_id,

            "emergency_id":
                emergency_id,

            "event_type":
                self.EVENT_TYPE,

            "status":
                final_status,

            "webhook_delivered":
                delivered,

            "webhook_failed":
                failed,
        }