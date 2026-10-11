import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_patient_e2e_lifecycle_journey(client: AsyncClient):
    """End-to-end integration test validating the entire interconnected 13-stage WellNexa AI workflow."""

    # 1. Registration & Authentication
    reg_resp = await client.post("/api/v1/auth/register", json={
        "email": "e2e_hero@example.com",
        "password": "Password123!",
        "first_name": "Natasha",
        "last_name": "Romanoff"
    })
    assert reg_resp.status_code == 201

    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "e2e_hero@example.com",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["data"]["access_token"]
    patient_id = login_resp.json()["data"]["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Unified Health Profile & Baseline Vitals
    await client.post("/api/v1/profile", json={
        "first_name": "Natasha",
        "last_name": "Romanoff",
        "gender": "FEMALE",
        "blood_group": "A_POSITIVE"
    }, headers=headers)
    await client.post("/api/v1/health-profile/allergies", json={"allergen": "Latex", "severity": "HIGH"}, headers=headers)
    await client.post("/api/v1/metrics", json={"metric_type": "HEIGHT_CM", "value": 170.0, "unit": "cm"}, headers=headers)
    await client.post("/api/v1/metrics", json={"metric_type": "WEIGHT_KG", "value": 60.0, "unit": "kg"}, headers=headers)
    await client.post("/api/v1/metrics", json={"metric_type": "BLOOD_PRESSURE_SYSTOLIC", "value": 118.0, "unit": "mmHg"}, headers=headers)

    # 3. Medical Document Upload & Lab Report Confirmation
    upload_resp = await client.post(
        "/api/v1/documents/upload",
        files={"file": ("lipid_panel.pdf", b"%PDF-1.4 Simulated Lipid Panel Content", "application/pdf")},
        data={"category": "LAB_REPORT", "title": "Annual Lipid Profile"},
        headers=headers
    )
    assert upload_resp.status_code == 201
    doc_id = upload_resp.json()["data"]["id"]

    ocr_resp = await client.post(f"/api/v1/reports/process-ocr/{doc_id}", headers=headers)
    assert ocr_resp.status_code == 200
    report_id = ocr_resp.json()["data"]["id"]

    confirm_resp = await client.post(f"/api/v1/reports/{report_id}/confirm", json={"notes": "Verified by patient"}, headers=headers)
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["data"]["status"] == "CONFIRMED"

    # 4. Prescription & Medication Dose Logging
    med_resp = await client.post("/api/v1/medicines", json={
        "name": "Vitamin D3",
        "dosage": "1000 IU",
        "form": "CAPSULE",
        "frequency": "ONCE_DAILY",
        "timing": "AFTER_MEAL",
        "stock_quantity": 30
    }, headers=headers)
    assert med_resp.status_code == 201
    med_id = med_resp.json()["data"]["id"]

    dose_resp = await client.post(f"/api/v1/medicines/{med_id}/log-dose", json={"status": "TAKEN"}, headers=headers)
    assert dose_resp.status_code == 200

    # 5. Smart Reminder Scheduling
    rem_resp = await client.post("/api/v1/reminders", json={
        "reminder_type": "WATER",
        "title": "Drink 500ml Water",
        "recurrence": "DAILY",
        "due_time": "11:00"
    }, headers=headers)
    assert rem_resp.status_code == 201

    # 6. Nutrition & Workout Logging
    meal_resp = await client.post("/api/v1/nutrition/meals", json={
        "meal_type": "LUNCH",
        "items": [
            {"food_name": "Grilled Chicken Salad", "serving_quantity": 1.0, "calories_kcal": 450.0, "protein_g": 38.0, "carbs_g": 20.0, "fat_g": 12.0}
        ]
    }, headers=headers)
    assert meal_resp.status_code == 201

    workout_resp = await client.post("/api/v1/fitness/workouts", json={
        "activity_type": "RUNNING",
        "title": "Afternoon Cardio Run",
        "duration_minutes": 35,
        "calories_burned": 320.0
    }, headers=headers)
    assert workout_resp.status_code == 201

    # 7. Mood Check-In
    mood_resp = await client.post("/api/v1/wellness/mood", json={
        "mood_score": 5,
        "primary_emotion": "FOCUSED",
        "gratitude_note": "Great workout and feeling balanced."
    }, headers=headers)
    assert mood_resp.status_code == 201

    # 8. Grounded AI Health Assistant Chat
    session_resp = await client.post("/api/v1/assistant/sessions", json={"title": "Nutrition Review"}, headers=headers)
    session_id = session_resp.json()["data"]["id"]

    msg_resp = await client.post(
        f"/api/v1/assistant/sessions/{session_id}/messages",
        json={"message": "How do my active Vitamin D supplements and lunch nutrition look?"},
        headers=headers
    )
    assert msg_resp.status_code == 200
    assert "Vitamin D" in msg_resp.json()["data"]["content"]

    # 9. Doctor Portal Sharing & Consultation Note
    grant_resp = await client.post("/api/v1/sharing/grants", json={
        "access_scope": "FULL_ACCESS",
        "duration_hours": 24,
        "notes": "Consultation with Sports Specialist"
    }, headers=headers)
    assert grant_resp.status_code == 201
    doc_token = grant_resp.json()["data"]["access_token"]

    doc_view = await client.get(f"/api/v1/doctor/patient/{patient_id}/summary?token={doc_token}")
    assert doc_view.status_code == 200
    assert any("Latex" in a for a in doc_view.json()["data"]["allergies"])

    consult_resp = await client.post(
        f"/api/v1/doctor/patient/{patient_id}/consultations?token={doc_token}",
        json={
            "doctor_name": "Dr. Stephen Strange",
            "chief_complaint": "Joint flexibility routine checkup",
            "clinical_observations": "Good vitals, clear chest, normal blood pressure.",
            "recommended_actions": "Maintain current fitness regimen."
        }
    )
    assert consult_resp.status_code == 201

    # 10. Intelligent Health Dashboard Verification
    dash_resp = await client.get("/api/v1/dashboard/home", headers=headers)
    assert dash_resp.status_code == 200
    dash_data = dash_resp.json()["data"]
    assert dash_data["medicines"]["taken_count"] >= 1
    assert dash_data["nutrition"]["calories_consumed"] == 450.0

    # 11. AI Health Snapshot
    snap_resp = await client.get("/api/v1/snapshot", headers=headers)
    assert snap_resp.status_code == 200
    assert snap_resp.json()["data"]["is_ai_generated"] is True

    # 12. Full Data Export
    export_resp = await client.get("/api/v1/privacy/export", headers=headers)
    assert export_resp.status_code == 200
    assert "Natasha" in str(export_resp.json()["data"]["profile"])
