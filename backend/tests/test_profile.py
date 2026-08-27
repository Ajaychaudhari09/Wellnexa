import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_profile_retrieval_and_update(client: AsyncClient):
    # Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "profile_user@example.com",
        "password": "Password123!",
        "first_name": "Bruce",
        "last_name": "Wayne"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "profile_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Retrieve Initial Profile
    prof_resp = await client.get("/api/v1/profile/me", headers=headers)
    assert prof_resp.status_code == 200
    prof_data = prof_resp.json()["data"]
    assert prof_data["first_name"] == "Bruce"
    assert prof_data["last_name"] == "Wayne"

    # Update Profile
    update_payload = {
        "first_name": "Bruce",
        "last_name": "Wayne",
        "phone_number": "+1234567890",
        "gender": "MALE",
        "blood_group": "O+",
        "emergency_contact_name": "Alfred Pennyworth",
        "emergency_contact_phone": "+1987654321"
    }
    update_resp = await client.put("/api/v1/profile/me", json=update_payload, headers=headers)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()["data"]
    assert updated_data["phone_number"] == "+1234567890"
    assert updated_data["blood_group"] == "O+"
    assert updated_data["emergency_contact_name"] == "Alfred Pennyworth"
