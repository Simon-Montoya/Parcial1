from uuid import UUID

from app.config.supabase_client import (
    get_supabase_client,
)


class NotificationRepository:

    def __init__(self):
        self.supabase = get_supabase_client()

    def emergency_exists(
        self,
        emergency_id: UUID,
    ) -> bool:

        response = (
            self.supabase
            .table("emergencies")
            .select("id")
            .eq("id", str(emergency_id))
            .limit(1)
            .execute()
        )

        return bool(response.data)

    def create_notification(
        self,
        emergency_id: UUID,
        message: str,
        event_type: str,
        payload: dict,
    ) -> dict:

        response = (
            self.supabase
            .table("notifications")
            .insert(
                {
                    "emergency_id":
                        str(emergency_id),

                    "message":
                        message,

                    "status":
                        "PENDING",

                    "event_type":
                        event_type,

                    "payload":
                        payload,
                }
            )
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Notification could not be created"
            )

        return response.data[0]

    def get_active_webhooks(
        self,
        event_type: str,
    ) -> list[dict]:

        response = (
            self.supabase
            .table("webhook_subscriptions")
            .select("*")
            .eq("active", True)
            .eq("event_type", event_type)
            .execute()
        )

        return response.data or []

    def create_webhook(
        self,
        url: str,
        event_type: str,
    ) -> dict:

        response = (
            self.supabase
            .table("webhook_subscriptions")
            .insert(
                {
                    "url": url,
                    "event_type": event_type,
                    "active": True,
                }
            )
            .execute()
        )

        return response.data[0]

    def record_delivery(
        self,
        notification_id: UUID,
        subscription_id: UUID,
        http_status: int | None,
        success: bool,
        error_message: str | None = None,
    ):

        (
            self.supabase
            .table("webhook_deliveries")
            .insert(
                {
                    "notification_id":
                        str(notification_id),

                    "subscription_id":
                        str(subscription_id),

                    "http_status":
                        http_status,

                    "success":
                        success,

                    "error_message":
                        error_message,
                }
            )
            .execute()
        )

    def update_notification_status(
        self,
        notification_id: UUID,
        status: str,
    ):

        (
            self.supabase
            .table("notifications")
            .update(
                {
                    "status": status
                }
            )
            .eq(
                "id",
                str(notification_id),
            )
            .execute()
        )