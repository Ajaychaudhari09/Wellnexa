import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_privacy_consent_export_and_deletion(client: AsyncClient):
    # 1. Register & Login Patient
    await client.post("/api/v1/auth/register", json={
        "email": "privacy_patient@example.com",
        "password": "Password123!",
        "first_name": "Wanda",
        "last_name": "Maximoff"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "privacy_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Add sample health data
    await client.post("/api/v1/health-profile/allergies", json={"allergen": "Dust Mites", "severity": "LOW"}, headers=headers)
    await client.post("/api/v1/fitness/daily-activity", json={"steps": 7500, "sleep_hours": 8.0}, headers=headers)

    # 2. Get & Update Consent Settings
    consent_get = await client.get("/api/v1/privacy/consent", headers=headers)
    assert consent_get.status_code == 200
    assert consent_get.json()["data"]["allow_ai_analysis"] is True

    consent_put = await client.put("/api/v1/privacy/consent", json={
        "allow_anonymized_insights": False,
        "data_retention_days": 180
    }, headers=headers)
    assert consent_put.status_code == 200
    assert consent_put.json()["data"]["allow_anonymized_insights"] is False
    assert consent_put.json()["data"]["data_retention_days"] == 180

    # 3. Export Full Health Archive
    export_resp = await client.get("/api/v1/privacy/export", headers=headers)
    assert export_resp.status_code == 200
    exp_data = export_resp.json()["data"]
    assert "Wanda" in str(exp_data["profile"])
    assert any("Dust Mites" in str(a) for a in exp_data["allergies"])

    # 4. Check Access Audit Logs
    logs_resp = await client.get("/api/v1/privacy/access-logs", headers=headers)
    assert logs_resp.status_code == 200
    logs_data = logs_resp.json()["data"]
    assert any(l["action"] == "EXPORT_HEALTH_DATA" for l in logs_data)

    # 5. Delete Account (Incorrect Password First)
    bad_del = await client.post("/api/v1/privacy/delete-account", json={"confirmation_password": "WrongPassword!"}, headers=headers)
    assert bad_del.status_code == 401

    # 6. Delete Account (Correct Password)
    good_del = await client.post("/api/v1/privacy/delete-account", json={"confirmation_password": "Password123!"}, headers=headers)
    assert good_del.status_code == 200
    assert good_del.json()["data"]["status"] == "DELETED"

    # 7. Verify Account is purged and cannot login
    re_login = await client.post("/api/v1/auth/login", json={"email": "privacy_patient@example.com", "password": "Password123!"})
    assert re_login.status_code == 401
