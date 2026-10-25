import pytest
from datetime import date, timedelta
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_appointment_lifecycle(client: AsyncClient):
    # Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "appointment_patient@wellnexa.ai",
        "password": "Password123!",
        "first_name": "Arthur",
        "last_name": "Dent"
    })
    login_res = await client.post("/api/v1/auth/login", json={
        "email": "appointment_patient@wellnexa.ai",
        "password": "Password123!"
    })
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Schedule appointment
    target_date = (date.today() + timedelta(days=5)).isoformat()
    req_data = {
        "doctor_name": "Dr. Sarah Connor, MD",
        "specialty": "Preventive Cardiology",
        "clinic_or_hospital": "Metropolitan Medical Institute",
        "location": "Suite 302, North Tower",
        "appointment_date": target_date,
        "appointment_time": "11:15 AM",
        "purpose": "Comprehensive Cardiovascular & Lipid Assessment",
        "notes": "Bring previous 3 months fasting glucose & BP log.",
        "appointment_type": "IN_PERSON",
    }
    create_res = await client.post("/api/v1/appointments", json=req_data, headers=headers)
    assert create_res.status_code == 201
    created_body = create_res.json()
    assert created_body["success"] is True
    app_id = created_body["data"]["id"]
    assert created_body["data"]["doctor_name"] == "Dr. Sarah Connor, MD"
    assert created_body["data"]["status"] == "SCHEDULED"

    # 2. List appointments
    list_res = await client.get("/api/v1/appointments", headers=headers)
    assert list_res.status_code == 200
    list_body = list_res.json()
    assert list_body["success"] is True
    items = list_body["data"]
    assert any(item["id"] == app_id for item in items)

    # 3. Update / Reschedule
    update_res = await client.patch(
        f"/api/v1/appointments/{app_id}",
        json={"appointment_time": "02:30 PM", "status": "CONFIRMED"},
        headers=headers,
    )
    assert update_res.status_code == 200
    updated_body = update_res.json()
    assert updated_body["data"]["appointment_time"] == "02:30 PM"
    assert updated_body["data"]["status"] == "CONFIRMED"

    # 4. Cancel appointment
    cancel_res = await client.delete(f"/api/v1/appointments/{app_id}", headers=headers)
    assert cancel_res.status_code == 200
    cancelled_body = cancel_res.json()
    assert cancelled_body["data"]["status"] == "CANCELLED"
