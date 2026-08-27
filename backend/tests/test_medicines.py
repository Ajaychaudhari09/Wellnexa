import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_prescription_and_medication_lifecycle(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "med_patient@example.com",
        "password": "Password123!",
        "first_name": "Steve",
        "last_name": "Rogers"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "med_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Prescription
    presc_resp = await client.post("/api/v1/prescriptions", json={
        "doctor_name": "Dr. Abraham Erskine",
        "clinic_name": "Project Rebirth Medical",
        "diagnosis_notes": "Post-training recovery regimen"
    }, headers=headers)
    assert presc_resp.status_code == 201
    presc_id = presc_resp.json()["data"]["id"]

    # 3. Add Medication with Schedules & Stock (Stock = 5, Refill Threshold = 5)
    med_payload = {
        "prescription_id": presc_id,
        "name": "Super Serum Boost",
        "dosage": "500 mg",
        "form": "TABLET",
        "frequency": "TWICE_DAILY",
        "timing": "AFTER_MEAL",
        "current_stock": 5,
        "refill_threshold": 5,
        "schedules": [
            {"time_slot": "09:00", "dosage_quantity": 1.0},
            {"time_slot": "21:00", "dosage_quantity": 1.0}
        ]
    }
    med_resp = await client.post("/api/v1/medicines", json=med_payload, headers=headers)
    assert med_resp.status_code == 201
    med_data = med_resp.json()["data"]
    med_id = med_data["id"]
    assert med_data["name"] == "Super Serum Boost"
    assert len(med_data["schedules"]) == 2

    # 4. Check Today's Schedule
    today_resp = await client.get("/api/v1/medicines/today", headers=headers)
    assert today_resp.status_code == 200
    today_data = today_resp.json()["data"]
    assert today_data["total_doses"] >= 2

    # 5. Log 3 TAKEN doses and 1 MISSED dose
    for _ in range(3):
        await client.post(f"/api/v1/medicines/{med_id}/log-dose", json={"status": "TAKEN"}, headers=headers)
    await client.post(f"/api/v1/medicines/{med_id}/log-dose", json={"status": "MISSED"}, headers=headers)

    # 6. Verify stock decremented: 5 initial - 3 taken = 2 remaining
    meds_list = await client.get("/api/v1/medicines", headers=headers)
    updated_med = next(m for m in meds_list.json()["data"] if m["id"] == med_id)
    assert updated_med["current_stock"] == 2

    # 7. Check Refill Alert (Stock 2 <= Threshold 5)
    refill_resp = await client.get("/api/v1/medicines/refills", headers=headers)
    assert refill_resp.status_code == 200
    refill_data = refill_resp.json()["data"]
    assert refill_data["total_alerts"] >= 1
    assert any(r["medication_id"] == med_id for r in refill_data["medications_requiring_refill"])

    # 8. Check Adherence Score: 3 taken / 4 total = 75.0% -> NEEDS_ATTENTION
    adh_resp = await client.get("/api/v1/medicines/adherence?days=30", headers=headers)
    assert adh_resp.status_code == 200
    adh_data = adh_resp.json()["data"]
    assert adh_data["total_taken"] == 3
    assert adh_data["total_missed"] == 1
    assert adh_data["overall_adherence_percentage"] == 75.0
    assert adh_data["adherence_tier"] == "NEEDS_ATTENTION"

    # 9. Verify Timeline has Medication Started and Dose Taken events
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    t_events = timeline_resp.json()["data"]["events"]
    assert any("Started Medication" in e["title"] for e in t_events)
    assert any("Dose Taken" in e["title"] for e in t_events)
