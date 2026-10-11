import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_fitness_workouts_activity_and_habits(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "fitness_user@example.com",
        "password": "Password123!",
        "first_name": "Tony",
        "last_name": "Stark"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "fitness_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Log a Workout
    workout_resp = await client.post("/api/v1/fitness/workouts", json={
        "activity_type": "STRENGTH_TRAINING",
        "title": "Upper Body Hypertrophy",
        "duration_minutes": 55,
        "calories_burned": 420.0,
        "intensity": "HIGH",
        "heart_rate_avg": 142,
        "notes": "Focused on chest and shoulders"
    }, headers=headers)
    assert workout_resp.status_code == 201
    workout_data = workout_resp.json()["data"]
    assert workout_data["duration_minutes"] == 55
    assert workout_data["calories_burned"] == 420.0

    # 3. Log Daily Lifestyle Activity (Steps, Sleep, Water, Stress)
    activity_resp = await client.post("/api/v1/fitness/daily-activity", json={
        "steps": 9450,
        "water_ml": 2800,
        "sleep_hours": 7.5,
        "sleep_quality": 4,
        "stress_level": 3
    }, headers=headers)
    assert activity_resp.status_code == 200
    act_data = activity_resp.json()["data"]
    assert act_data["steps"] == 9450
    assert act_data["active_minutes"] >= 55 # Added from workout
    assert act_data["calories_burned"] >= 420.0

    # 4. Create a Habit
    habit_resp = await client.post("/api/v1/fitness/habits", json={
        "title": "Morning Meditation",
        "description": "10 minutes mindfulness before work",
        "category": "Mindfulness",
        "frequency": "DAILY"
    }, headers=headers)
    assert habit_resp.status_code == 201
    habit_data = habit_resp.json()["data"]
    habit_id = habit_data["id"]
    assert habit_data["current_streak"] == 0

    # 5. Check in Habit
    checkin_resp = await client.post(f"/api/v1/fitness/habits/{habit_id}/check-in", json={"is_completed": True}, headers=headers)
    assert checkin_resp.status_code == 200
    assert checkin_resp.json()["data"]["current_streak"] == 1

    # 6. Retrieve Habits List & Check today's status
    habits_list = await client.get("/api/v1/fitness/habits", headers=headers)
    assert habits_list.status_code == 200
    h_item = next(h for h in habits_list.json()["data"] if h["id"] == habit_id)
    assert h_item["is_completed_today"] is True
    assert h_item["current_streak"] == 1

    # 7. Check Weekly Trends
    trends_resp = await client.get("/api/v1/fitness/trends?days=7", headers=headers)
    assert trends_resp.status_code == 200
    t_data = trends_resp.json()["data"]
    assert len(t_data["trends"]) == 7
    assert t_data["average_daily_steps"] > 0

    # 8. Check Timeline for Workout Completed event
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    t_events = timeline_resp.json()["data"]["events"]
    assert any("Workout" in e["title"] for e in t_events)
