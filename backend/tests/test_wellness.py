import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_mood_logging_trends_and_crisis_safety(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "wellness_user@example.com",
        "password": "Password123!",
        "first_name": "Bruce",
        "last_name": "Banner"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "wellness_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Log Standard Positive Mood Entry
    mood1 = await client.post("/api/v1/wellness/mood", json={
        "mood_score": 4,
        "primary_emotion": "CALM",
        "tags": ["Meditation", "Good Sleep"],
        "journal_text": "Spent 20 minutes doing breathing exercises. Feeling grounded and peaceful.",
        "gratitude_note": "Grateful for a quiet morning and supportive team.",
        "sleep_quality": 4
    }, headers=headers)
    assert mood1.status_code == 201
    m1_data = mood1.json()["data"]
    assert m1_data["mood_score"] == 4
    assert m1_data["primary_emotion"] == "CALM"
    assert m1_data["crisis_flag"] is False
    assert m1_data["crisis_support"] is None

    # 3. Check Today's Mood
    today_resp = await client.get("/api/v1/wellness/mood/today", headers=headers)
    assert today_resp.status_code == 200
    assert today_resp.json()["data"]["mood_score"] == 4

    # 4. Check Weekly Mood Trends
    trends_resp = await client.get("/api/v1/wellness/mood/trends?days=7", headers=headers)
    assert trends_resp.status_code == 200
    t_data = trends_resp.json()["data"]
    assert t_data["average_mood_score"] >= 4.0
    assert len(t_data["trends"]) == 7

    # 5. Test Crisis Detection Safety Guardrail
    crisis_entry = await client.post("/api/v1/wellness/mood", json={
        "mood_score": 1,
        "primary_emotion": "OVERWHELMED",
        "tags": ["Crisis"],
        "journal_text": "I feel hopeless and I want to end my life. Everything is too much.",
        "sleep_quality": 1
    }, headers=headers)
    assert crisis_entry.status_code == 201
    c_data = crisis_entry.json()["data"]
    assert c_data["crisis_flag"] is True
    assert c_data["crisis_support"] is not None
    assert "Tele-MANAS" in str(c_data["crisis_support"]["helpline_resources"])

    # 6. Check Timeline for Wellness Logged event
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    t_events = timeline_resp.json()["data"]["events"]
    assert any("Mood Logged" in e["title"] for e in t_events)
