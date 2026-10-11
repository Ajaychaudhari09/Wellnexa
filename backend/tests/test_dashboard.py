import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_intelligent_health_dashboard_aggregation(client: AsyncClient):
    # 1. Register & Login Patient
    await client.post("/api/v1/auth/register", json={
        "email": "dash_patient@example.com",
        "password": "Password123!",
        "first_name": "Carol",
        "last_name": "Danvers"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "dash_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed Data Across Modules
    # Vitals (Height 175cm, Weight 68kg -> BMI auto-calculated ~22.2)
    await client.post("/api/v1/metrics", json={"metric_type": "HEIGHT_CM", "value": 175.0, "unit": "cm"}, headers=headers)
    await client.post("/api/v1/metrics", json={"metric_type": "WEIGHT_KG", "value": 68.0, "unit": "kg"}, headers=headers)
    await client.post("/api/v1/metrics", json={"metric_type": "BLOOD_GLUCOSE_FASTING", "value": 92.0, "unit": "mg/dL"}, headers=headers)

    # Medicine
    await client.post("/api/v1/medicines", json={
        "name": "Omega-3 Fish Oil",
        "dosage": "1000 mg",
        "form": "CAPSULE",
        "frequency": "ONCE_DAILY",
        "timing": "AFTER_MEAL"
    }, headers=headers)

    # Reminder
    await client.post("/api/v1/reminders", json={
        "reminder_type": "WATER",
        "title": "Drink 500ml Water",
        "recurrence": "DAILY",
        "due_time": "10:30"
    }, headers=headers)

    # Nutrition Meal
    await client.post("/api/v1/nutrition/meals", json={
        "meal_type": "BREAKFAST",
        "items": [
            {"food_name": "Oatmeal with Berries", "serving_quantity": 1.0, "calories_kcal": 350.0, "protein_g": 12.0, "carbs_g": 55.0, "fat_g": 6.0}
        ]
    }, headers=headers)

    # Mood Check-in
    await client.post("/api/v1/wellness/mood", json={
        "mood_score": 5,
        "primary_emotion": "ENERGETIC",
        "gratitude_note": "Feeling powerful and ready for the day!"
    }, headers=headers)

    # 3. Call Unified Home Dashboard Endpoint
    dash_resp = await client.get("/api/v1/dashboard/home", headers=headers)
    assert dash_resp.status_code == 200
    data = dash_resp.json()["data"]

    # Verify Profile Header
    assert "Carol" in data["profile"]["first_name"]
    assert "Danvers" in data["profile"]["last_name"]

    # Verify Medicines Widget
    assert data["medicines"]["total_scheduled"] >= 1
    assert data["medicines"]["pending_count"] >= 1

    # Verify Reminders Widget
    assert data["reminders"]["total_due"] >= 1

    # Verify Vitals & BMI
    assert data["vitals"]["bmi"] is not None
    assert data["vitals"]["bmi_category"] == "Normal"

    # Verify Nutrition Widget
    assert data["nutrition"]["calories_consumed"] == 350.0
    assert data["nutrition"]["meals_logged_count"] == 1

    # Verify Mood Widget
    assert data["mood"]["is_logged_today"] is True
    assert data["mood"]["mood_score"] == 5
    assert data["mood"]["primary_emotion"] == "ENERGETIC"

    # Verify Adherence Widget
    assert "adherence_percentage" in data["adherence"]

    # Verify Quick Actions
    assert len(data["quick_actions"]) == 5
    action_ids = [a["id"] for a in data["quick_actions"]]
    assert "log_vitals" in action_ids
    assert "chat_ai" in action_ids
