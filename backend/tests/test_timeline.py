import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_timeline_auto_generation_and_feed(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "timeline_user@example.com",
        "password": "Password123!",
        "first_name": "Barry",
        "last_name": "Allen"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "timeline_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Log Vitals (Systolic BP and Weight)
    await client.post("/api/v1/metrics", json={
        "metrics": [
            {"metric_type": "BLOOD_PRESSURE_SYSTOLIC", "value": 118.0, "unit": "mmHg"},
            {"metric_type": "WEIGHT", "value": 75.0, "unit": "kg"},
        ]
    }, headers=headers)

    # 3. Add Condition
    await client.post("/api/v1/health-profile/conditions", json={
        "condition_name": "Runner's Knee",
        "status": "MANAGED"
    }, headers=headers)

    # 4. Create a custom milestone
    custom_resp = await client.post("/api/v1/timeline/custom", json={
        "category": "FITNESS",
        "title": "Completed 10k Run",
        "summary": "Finished marathon training session in 48 minutes"
    }, headers=headers)
    assert custom_resp.status_code == 201
    custom_event_id = custom_resp.json()["data"]["id"]

    # 5. Fetch Timeline Feed
    feed_resp = await client.get("/api/v1/timeline", headers=headers)
    assert feed_resp.status_code == 200
    feed_data = feed_resp.json()["data"]
    events = feed_data["events"]
    
    # We should have events for metrics, condition, and custom milestone
    assert len(events) >= 3
    event_titles = [e["title"] for e in events]
    assert any("Blood Pressure Systolic" in t for t in event_titles)
    assert any("Runner's Knee" in e["summary"] or "Medical Condition Logged" in e["title"] for e in events)
    assert "Completed 10k Run" in event_titles

    # 6. Test Pinning Event
    pin_resp = await client.patch(f"/api/v1/timeline/{custom_event_id}/pin", json={"is_pinned": True}, headers=headers)
    assert pin_resp.status_code == 200
    assert pin_resp.json()["data"]["is_pinned"] is True

    # 7. Test Category Filtering
    filter_resp = await client.get("/api/v1/timeline?category=FITNESS", headers=headers)
    assert filter_resp.status_code == 200
    fitness_events = filter_resp.json()["data"]["events"]
    assert len(fitness_events) >= 1
    assert all(e["category"] == "FITNESS" for e in fitness_events)
