from app.config.supabase_client import get_supabase_client
from app.models.emergency import EmergencyCreate, EmergencyType


class EmergencyRepository:

    def __init__(self):
        self.supabase = get_supabase_client()

    def create_emergency(
        self,
        emergency: EmergencyCreate,
        priority: str
    ) -> dict:

        emergency_data = {
            "type": emergency.type.value,
            "priority": priority,
            "status": "RECEIVED",
            "city": emergency.city.value,
            "description": emergency.description,
            "latitude": emergency.latitude,
            "longitude": emergency.longitude
        }

        response = (
            self.supabase
            .table("emergencies")
            .insert(emergency_data)
            .execute()
        )

        if not response.data:
            raise RuntimeError(
                "Emergency could not be created"
            )

        created_emergency = response.data[0]

        print("TYPE RECEIVED:", emergency.type)
        print("IS RESCUE:", emergency.type == EmergencyType.RESCUE)

        if emergency.type == EmergencyType.RESCUE:

            rescue_data = {
                "emergency_id": created_emergency["id"],
                "trapped_people": emergency.trapped_people,
                "injured_people": emergency.injured_people,
                "gas_leak": emergency.gas_leak,
                "fire": emergency.fire,
                "imminent_collapse_risk":
                    emergency.imminent_collapse_risk
            }

            print("CREATED EMERGENCY:", created_emergency)
            print("RESCUE DATA:", rescue_data)

            rescue_response = (
                self.supabase
                .table("rescue_details")
                .insert(rescue_data)
                .execute()
            )

            print("RESCUE RESPONSE:", rescue_response)

            if not rescue_response.data:
                raise RuntimeError(
                    "Rescue details could not be created"
                )

        return created_emergency