import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_ai_health_snapshot_generation(client: AsyncClient):
    # 1. Register & Login Patient
    await client.post("/api/v1/auth/register", json={
        "email": "snapshot_patient@example.com",
        "password": "Password123!",
        "first_name": "Scott",
        "last_name": "Lang"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "snapshot_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed Positive and Focus Metrics
    # Healthy BMI
    await client.post("/api/v1/metrics", json={"metric_type": "HEIGHT_CM", "value": 178.0, "unit": "cm"}, headers=headers)
    await client.post("/api/v1/metrics", json={"metric_type": "WEIGHT_KG", "value": 72.0, "unit": "kg"}, headers=headers)

    # Medicine with perfect adherence (3 doses taken)
    med_resp = await client.post("/api/v1/medicines", json={
        "name": "Pym Particles Tonic",
        "dosage": "50 mg",
        "form": "SYRUP",
        "frequency": "ONCE_DAILY",
        "timing": "AFTER_MEAL"
    }, headers=headers)
    med_id = med_resp.json()["data"]["id"]
    for _ in range(3):
        await client.post(f"/api/v1/medicines/{med_id}/log-dose", json={"status": "TAKEN"}, headers=headers)

    # Fitness: High daily steps
    await client.post("/api/v1/fitness/daily-activity", json={"steps": 8500, "sleep_hours": 7.5}, headers=headers)

    # 3. Retrieve AI Health Snapshot
    snapshot_resp = await client.get("/api/v1/snapshot", headers=headers)
    assert snapshot_resp.status_code == 200
    snap_data = snapshot_resp.json()["data"]

    # Verify Snapshot Content
    assert snap_data["patient_name"] == "Scott"
    assert snap_data["is_ai_generated"] is True
    assert len(snap_data["positive_trends"]) >= 2 # BMI + Adherence + Steps
    assert any("adherence" in t.lower() for t in snap_data["positive_trends"])
    assert len(snap_data["suggested_next_actions"]) >= 1
    assert "disclaimer" in snap_data["medical_disclaimer"].lower()
