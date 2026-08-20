from datetime import date
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def patient_payload():
    return {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "1995-04-10",
        "sex": "Female",
        "phone_number": "4155550123",
        "email": "jane@example.com",
        "address_line_1": "123 Main Street",
        "city": "San Francisco",
        "state": "CA",
        "zip_code": "94105",
        "preferred_language": "English",
    }


def test_create_and_get_patient():
    payload = patient_payload()

    create = client.post("/patients", json=payload)
    assert create.status_code == 201

    body = create.json()
    assert body["error"] is None
    patient_id = body["data"]["patient_id"]

    get = client.get(f"/patients/{patient_id}")
    assert get.status_code == 200
    assert get.json()["data"]["first_name"] == "Jane"


def test_invalid_future_dob():
    payload = patient_payload()
    payload["date_of_birth"] = "2999-01-01"

    response = client.post("/patients", json=payload)
    assert response.status_code == 422
