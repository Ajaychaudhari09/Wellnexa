import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_and_login_success(client: AsyncClient):
    # 1. Register
    reg_payload = {
        "email": "patient@example.com",
        "password": "StrongPassword123!",
        "first_name": "John",
        "last_name": "Doe",
        "role": "PATIENT"
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["email"] == "patient@example.com"
    assert "PATIENT" in reg_data["data"]["roles"]

    # 2. Login
    login_payload = {
        "email": "patient@example.com",
        "password": "StrongPassword123!"
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is True
    assert "access_token" in login_data["data"]
    assert "refresh_token" in login_data["data"]

    access_token = login_data["data"]["access_token"]
    refresh_token = login_data["data"]["refresh_token"]

    # 3. Access Protected /me
    headers = {"Authorization": f"Bearer {access_token}"}
    me_resp = await client.get("/api/v1/auth/me", headers=headers)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["data"]["email"] == "patient@example.com"

    # 4. Refresh token
    ref_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    assert "access_token" in ref_data["data"]

    # 5. Logout
    logout_resp = await client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token}, headers=headers)
    assert logout_resp.status_code == 200

@pytest.mark.asyncio
async def test_duplicate_registration_fails(client: AsyncClient):
    reg_payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "first_name": "Jane",
        "last_name": "Smith",
    }
    resp1 = await client.post("/api/v1/auth/register", json=reg_payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/auth/register", json=reg_payload)
    assert resp2.status_code == 409

@pytest.mark.asyncio
async def test_invalid_login_fails(client: AsyncClient):
    reg_payload = {
        "email": "user@example.com",
        "password": "CorrectPassword123!",
        "first_name": "Alice",
        "last_name": "Wonder",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_resp = await client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "WrongPassword"})
    assert login_resp.status_code == 401

@pytest.mark.asyncio
async def test_rbac_doctor_route_access(client: AsyncClient):
    # Register Patient
    patient_payload = {
        "email": "patient_only@example.com",
        "password": "Password123!",
        "first_name": "Pat",
        "last_name": "Ient",
        "role": "PATIENT"
    }
    await client.post("/api/v1/auth/register", json=patient_payload)
    p_login = await client.post("/api/v1/auth/login", json={"email": "patient_only@example.com", "password": "Password123!"})
    p_token = p_login.json()["data"]["access_token"]

    # Patient accessing doctor endpoint should be 403 Forbidden
    doc_attempt = await client.get("/api/v1/auth/doctor-only", headers={"Authorization": f"Bearer {p_token}"})
    assert doc_attempt.status_code == 403

    # Public registration must never permit self-assigned doctor/admin access.
    doc_payload = {
        "email": "doctor@example.com",
        "password": "Password123!",
        "first_name": "Doc",
        "last_name": "Tor",
        "role": "DOCTOR"
    }
    doctor_register = await client.post("/api/v1/auth/register", json=doc_payload)
    assert doctor_register.status_code == 403

    admin_payload = {**doc_payload, "email": "admin@example.com", "role": "ADMIN"}
    admin_register = await client.post("/api/v1/auth/register", json=admin_payload)
    assert admin_register.status_code == 403
