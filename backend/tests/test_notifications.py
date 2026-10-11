import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_notifications_dispatch_read_and_unread_counts(client: AsyncClient):
    # 1. Register & Login Patient
    await client.post("/api/v1/auth/register", json={
        "email": "notif_patient@example.com",
        "password": "Password123!",
        "first_name": "Hope",
        "last_name": "Van Dyne"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "notif_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Check initial unread count (should be 0)
    c0_resp = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert c0_resp.status_code == 200
    assert c0_resp.json()["data"]["unread_count"] == 0

    # 3. Dispatch 2 Test Notifications (Medicine Due & Refill Alert)
    n1_resp = await client.post("/api/v1/notifications/test-dispatch", json={
        "notification_type": "MEDICINE_DUE",
        "title": "Time for Evening Metformin",
        "body": "Please take your 500mg dose after dinner.",
        "priority": "HIGH"
    }, headers=headers)
    assert n1_resp.status_code == 201
    n1_id = n1_resp.json()["data"]["id"]

    n2_resp = await client.post("/api/v1/notifications/test-dispatch", json={
        "notification_type": "REFILL_ALERT",
        "title": "Low Stock Warning: Vitamin D",
        "body": "Only 3 tablets remaining. Please request a pharmacy refill.",
        "priority": "NORMAL"
    }, headers=headers)
    assert n2_resp.status_code == 201

    # 4. Check Unread Count (should be 2)
    c2_resp = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert c2_resp.status_code == 200
    assert c2_resp.json()["data"]["unread_count"] == 2

    # 5. Mark Single Notification as Read
    read_resp = await client.post(f"/api/v1/notifications/{n1_id}/read", headers=headers)
    assert read_resp.status_code == 200
    assert read_resp.json()["data"]["is_read"] is True

    # Check unread count is now 1
    c1_resp = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert c1_resp.status_code == 200
    assert c1_resp.json()["data"]["unread_count"] == 1

    # 6. Mark All as Read
    all_read_resp = await client.post("/api/v1/notifications/mark-all-read", headers=headers)
    assert all_read_resp.status_code == 200
    assert all_read_resp.json()["data"]["updated_count"] >= 1

    # Check unread count is now 0
    final_count = await client.get("/api/v1/notifications/unread-count", headers=headers)
    assert final_count.status_code == 200
    assert final_count.json()["data"]["unread_count"] == 0
