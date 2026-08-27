import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_metrics_logging_and_bmi_calculation(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "metrics_user@example.com",
        "password": "Password123!",
        "first_name": "Tony",
        "last_name": "Stark"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "metrics_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Log Height (180 cm) and Weight (80 kg)
    metrics_payload = {
        "metrics": [
            {"metric_type": "HEIGHT", "value": 180.0, "unit": "cm", "source": "MANUAL"},
            {"metric_type": "WEIGHT", "value": 81.0, "unit": "kg", "source": "MANUAL"},
            {"metric_type": "BLOOD_PRESSURE_SYSTOLIC", "value": 120.0, "unit": "mmHg", "source": "MANUAL"},
            {"metric_type": "BLOOD_PRESSURE_DIASTOLIC", "value": 80.0, "unit": "mmHg", "source": "MANUAL"},
        ]
    }
    log_resp = await client.post("/api/v1/metrics", json=metrics_payload, headers=headers)
    assert log_resp.status_code == 201
    assert log_resp.json()["success"] is True

    # 3. Retrieve all metrics and check auto-calculated BMI
    # BMI = 81 / (1.80^2) = 81 / 3.24 = 25.0
    get_resp = await client.get("/api/v1/metrics", headers=headers)
    assert get_resp.status_code == 200
    metrics_list = get_resp.json()["data"]
    
    metric_types = [m["metric_type"] for m in metrics_list]
    assert "HEIGHT" in metric_types
    assert "WEIGHT" in metric_types
    assert "BMI" in metric_types
    
    bmi_entry = next(m for m in metrics_list if m["metric_type"] == "BMI")
    assert bmi_entry["value"] == 25.0
    assert bmi_entry["source"] == "SYSTEM_CALCULATED"

    # 4. Check Trend Endpoint for Blood Pressure
    trend_resp = await client.get("/api/v1/metrics/trends/BLOOD_PRESSURE_SYSTOLIC?days=30", headers=headers)
    assert trend_resp.status_code == 200
    trend_data = trend_resp.json()["data"]
    assert trend_data["metric_type"] == "BLOOD_PRESSURE_SYSTOLIC"
    assert trend_data["latest_value"] == 120.0
    assert len(trend_data["data_points"]) == 1

@pytest.mark.asyncio
async def test_allergies_conditions_goals_and_summary(client: AsyncClient):
    # Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "clinical_user@example.com",
        "password": "Password123!",
        "first_name": "Clark",
        "last_name": "Kent"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "clinical_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add Allergy
    allergy_resp = await client.post("/api/v1/health-profile/allergies", json={
        "allergen": "Penicillin",
        "reaction": "Skin rash and hives",
        "severity": "SEVERE",
        "is_active": True
    }, headers=headers)
    assert allergy_resp.status_code == 201
    allergy_id = allergy_resp.json()["data"]["id"]

    # Add Medical Condition
    cond_resp = await client.post("/api/v1/health-profile/conditions", json={
        "condition_name": "Mild Seasonal Allergies",
        "diagnosed_date": "2024-03-15",
        "status": "MANAGED",
        "notes": "Under control with antihistamines"
    }, headers=headers)
    assert cond_resp.status_code == 201

    # Add Health Goal
    goal_resp = await client.post("/api/v1/health-profile/goals", json={
        "title": "Maintain Hydration",
        "goal_type": "WATER_INTAKE",
        "target_value": 3.0,
        "current_value": 2.2,
        "unit": "Liters",
        "status": "IN_PROGRESS"
    }, headers=headers)
    assert goal_resp.status_code == 201

    # Update Lifestyle
    life_resp = await client.put("/api/v1/health-profile/lifestyle", json={
        "diet_type": "VEGETARIAN",
        "activity_level": "MODERATE",
        "smoking_status": "NON_SMOKER",
        "sleep_target_hours": 8.0,
        "water_target_liters": 3.0
    }, headers=headers)
    assert life_resp.status_code == 200
    assert life_resp.json()["data"]["diet_type"] == "VEGETARIAN"

    # Get Unified Summary
    summary_resp = await client.get("/api/v1/health-profile/summary", headers=headers)
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()["data"]
    assert len(summary_data["active_allergies"]) == 1
    assert summary_data["active_allergies"][0]["allergen"] == "Penicillin"
    assert len(summary_data["active_conditions"]) == 1
    assert len(summary_data["active_goals"]) == 1
    assert summary_data["lifestyle"]["diet_type"] == "VEGETARIAN"

    # Delete Allergy
    del_resp = await client.delete(f"/api/v1/health-profile/allergies/{allergy_id}", headers=headers)
    assert del_resp.status_code == 200

    # Verify Allergy is gone
    get_allergies_resp = await client.get("/api/v1/health-profile/allergies", headers=headers)
    assert len(get_allergies_resp.json()["data"]) == 0
