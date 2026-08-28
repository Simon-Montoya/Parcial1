from app.models.emergency import EmergencyCreate
from app.repositories.emergency_repository import EmergencyRepository


class FakeTable:
    def __init__(self, name, calls):
        self.name = name
        self.calls = calls
        self.data = None

    def insert(self, data):
        self.data = data
        return self

    def execute(self):
        self.calls.append((self.name, self.data))
        return type("Response", (), {"data": [self.data]})()


class FakeSupabase:
    def __init__(self):
        self.calls = []

    def table(self, name):
        return FakeTable(name, self.calls)


def create_repository():
    repository = EmergencyRepository.__new__(EmergencyRepository)
    repository.supabase = FakeSupabase()
    return repository


def test_rescue_uses_rescue_details_contract():
    repository = create_repository()
    emergency = EmergencyCreate(**{
        "type": "RESCUE", "city": "CALI", "latitude": 3.45,
        "longitude": -76.53, "trapped_people": 2,
        "injured_people": 1, "gas_leak": True,
        "fire": False, "imminent_collapse_risk": True,
    })

    repository._create_emergency_details("emergency-id", emergency)

    table, data = repository.supabase.calls[-1]
    assert table == "rescue_details"
    assert data["trapped_people"] == 2
    assert data["imminent_collapse_risk"] is True


def test_shelter_uses_shelter_details_contract():
    repository = create_repository()
    emergency = EmergencyCreate(**{
        "type": "SHELTER", "city": "CALI", "latitude": 3.45,
        "longitude": -76.53, "adults": 2, "children": 1,
        "elderly": 1, "accessibility_required": True,
        "house_habitable": False,
    })

    repository._create_emergency_details("emergency-id", emergency)

    table, data = repository.supabase.calls[-1]
    assert table == "shelter_details"
    assert data["adults"] == 2
    assert data["house_habitable"] is False


def test_supply_uses_supply_details_contract():
    repository = create_repository()
    emergency = EmergencyCreate(**{
        "type": "SUPPLY", "city": "CALI", "latitude": 3.45,
        "longitude": -76.53, "supply_category": "FIRST_AID",
        "quantity": 5, "notes": "Bandages",
    })

    repository._create_emergency_details("emergency-id", emergency)

    table, data = repository.supabase.calls[-1]
    assert table == "supply_details"
    assert data["supply_category"] == "FIRST_AID"
    assert data["quantity"] == 5


def test_structural_damage_uses_structural_details_contract():
    repository = create_repository()
    emergency = EmergencyCreate(**{
        "type": "STRUCTURAL_DAMAGE", "city": "CALI",
        "latitude": 3.45, "longitude": -76.53,
        "building_type": "BRIDGE", "cracking_level": "HIGH",
        "settlement_level": "MEDIUM", "collapse_risk": True,
        "road_risk": True, "photo_url": "https://example.com/photo.jpg",
    })

    repository._create_emergency_details("emergency-id", emergency)

    table, data = repository.supabase.calls[-1]
    assert table == "structural_damage_details"
    assert data["building_type"] == "BRIDGE"
    assert data["collapse_risk"] is True
