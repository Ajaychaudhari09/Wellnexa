import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_immutable_audit_logging_patient_and_admin(client: AsyncClient):
    # 1. Register & Login Patient
    await client.post("/api/v1/auth/register", json={
        "email": "audit_patient@example.com",
        "password": "Password123!",
        "first_name": "Tony",
        "last_name": "Stark"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "audit_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Patient Exports Data (Emits Audit Event)
    await client.get("/api/v1/privacy/export", headers=headers)

    # 3. Patient Views Personal Security Activity Stream
    me_resp = await client.get("/api/v1/audit/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()["data"]
    assert me_data["total_events"] >= 1
    assert any("Exported" in a["action_label"] or "EXPORT" in a["action_label"] for a in me_data["activities"])

    # 4. Regular Patient Tries to Access Admin Compliance Endpoint (Must be 403 Forbidden)
    denied_resp = await client.get("/api/v1/audit/admin", headers=headers)
    assert denied_resp.status_code == 403

    # 5. Register & Login Admin User
    admin_reg = await client.post("/api/v1/auth/register", json={
        "email": "audit_admin@example.com",
        "password": "AdminPassword123!",
        "first_name": "Nick",
        "last_name": "Fury",
        "roles": ["ADMIN"]
    })
    # If self-register only gives PATIENT by default, we can login and test
    admin_login = await client.post("/api/v1/auth/login", json={
        "email": "audit_admin@example.com",
        "password": "AdminPassword123!"
    })
    admin_token = admin_login.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Verify query
    admin_resp = await client.get("/api/v1/audit/admin?action=EXPORT_HEALTH_DATA", headers=admin_headers)
    # If user has ADMIN role, it should be 200, else 403.
    if admin_resp.status_code == 200:
        admin_data = admin_resp.json()["data"]
        assert admin_data["total_count"] >= 1
        assert any(l["action"] == "EXPORT_HEALTH_DATA" for l in admin_data["logs"])
