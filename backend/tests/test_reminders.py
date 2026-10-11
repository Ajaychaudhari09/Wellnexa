import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_reminders_lifecycle_action_and_preferences(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "reminder_user@example.com",
        "password": "Password123!",
        "first_name": "Diana",
        "last_name": "Prince"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "reminder_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Reminders (Medicine & Water)
    med_rem = await client.post("/api/v1/reminders", json={
        "reminder_type": "MEDICINE",
        "title": "Morning Vitamin D",
        "recurrence": "DAILY",
        "due_time": "08:30"
    }, headers=headers)
    assert med_rem.status_code == 201
    med_rem_id = med_rem.json()["data"]["id"]

    water_rem = await client.post("/api/v1/reminders", json={
        "reminder_type": "WATER",
        "title": "Hydration Break (500ml)",
        "recurrence": "DAILY",
        "due_time": "11:00"
    }, headers=headers)
    assert water_rem.status_code == 201

    # 3. Check Today's Due Reminders
    today_resp = await client.get("/api/v1/reminders/today", headers=headers)
    assert today_resp.status_code == 200
    today_data = today_resp.json()["data"]
    assert today_data["total_due"] >= 2
    assert today_data["pending_count"] >= 2

    # 4. Mark Medicine Reminder as COMPLETED
    action_resp = await client.post(f"/api/v1/reminders/{med_rem_id}/action", json={
        "status": "COMPLETED",
        "notes": "Taken with breakfast"
    }, headers=headers)
    assert action_resp.status_code == 200
    assert action_resp.json()["data"]["status"] == "COMPLETED"

    # 5. Check Today's Schedule to verify completion status updated
    today_updated = await client.get("/api/v1/reminders/today", headers=headers)
    assert today_updated.status_code == 200
    today_u_data = today_updated.json()["data"]
    assert today_u_data["completed_count"] >= 1

    # 6. Verify Timeline event is emitted for completion
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    t_events = timeline_resp.json()["data"]["events"]
    assert any("Reminder Completed" in e["title"] for e in t_events)

    # 7. Notification Preferences
    pref_get = await client.get("/api/v1/reminders/preferences", headers=headers)
    assert pref_get.status_code == 200
    assert pref_get.json()["data"]["medicine_alerts"] is True

    # Update Preferences
    pref_update = await client.put("/api/v1/reminders/preferences", json={
        "enable_email": True,
        "quiet_hours_start": "23:00",
        "quiet_hours_end": "06:00"
    }, headers=headers)
    assert pref_update.status_code == 200
    assert pref_update.json()["data"]["enable_email"] is True
    assert pref_update.json()["data"]["quiet_hours_start"] == "23:00"
