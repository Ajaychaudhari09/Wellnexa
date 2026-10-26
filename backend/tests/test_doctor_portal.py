import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_doctor_portal_sharing_and_consultations(client: AsyncClient):
    # 1. Register & Login Patient
    await client.post("/api/v1/auth/register", json={
        "email": "doctor_patient@example.com",
        "password": "Password123!",
        "first_name": "Clint",
        "last_name": "Barton"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "doctor_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    patient_id = login_resp.json()["data"]["user"]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    consent_resp = await client.put("/api/v1/privacy/consent", json={"allow_doctor_sharing": True}, headers=headers)
    assert consent_resp.status_code == 200

    # Add an allergy and active medication
    await client.post("/api/v1/health-profile/allergies", json={"allergen": "Penicillin", "severity": "HIGH"}, headers=headers)
    await client.post("/api/v1/medicines", json={
        "name": "Ibuprofen",
        "dosage": "400 mg",
        "form": "TABLET",
        "frequency": "AS_NEEDED",
        "timing": "AFTER_MEAL"
    }, headers=headers)

    # Provision an approved doctor in the test database.
    from sqlalchemy import select
    from app.models.user import User, Role, RoleEnum
    from app.core.security import get_password_hash
    from tests.conftest import TestingSessionLocal
    async with TestingSessionLocal() as db:
        doctor_role = (await db.execute(select(Role).where(Role.name == RoleEnum.DOCTOR))).scalar_one_or_none()
        if doctor_role is None:
            doctor_role = Role(name=RoleEnum.DOCTOR, description="Approved test doctor")
            db.add(doctor_role)
            await db.flush()
        doctor = User(email="approved-doctor@example.com", hashed_password=get_password_hash("Password123!"), is_active=True, is_verified=True, roles=[doctor_role])
        db.add(doctor)
        await db.commit()

    doctor_login = await client.post("/api/v1/auth/login", json={"email": "approved-doctor@example.com", "password": "Password123!"})
    doctor_headers = {"Authorization": f"Bearer {doctor_login.json()['data']['access_token']}"}

    # 2. Patient grants only this named doctor temporary access.
    grant_resp = await client.post("/api/v1/sharing/grants", json={
        "access_scope": "FULL_ACCESS", "duration_hours": 24,
        "doctor_email": "approved-doctor@example.com",
        "notes": "Access grant for Annual Orthopedic Checkup"
    }, headers=headers)
    assert grant_resp.status_code == 201
    grant_data = grant_resp.json()["data"]
    grant_id = grant_data["id"]
    access_token = grant_data["access_token"]
    assert grant_data["status"] == "ACTIVE"

    anonymous_summary = await client.get(f"/api/v1/doctor/patient/{patient_id}/summary?token={access_token}")
    assert anonymous_summary.status_code == 401

    # 3. Doctor Uses Assigned Access Token to View Patient Clinical Summary
    summary_resp = await client.get(f"/api/v1/doctor/patient/{patient_id}/summary?token={access_token}", headers=doctor_headers)
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()["data"]
    assert "Clint Barton" in summary_data["full_name"]
    assert any("Penicillin" in a for a in summary_data["allergies"])
    assert any("Ibuprofen" in m["name"] for m in summary_data["active_medications"])

    # 4. Doctor Records Consultation Notes
    consult_resp = await client.post(
        f"/api/v1/doctor/patient/{patient_id}/consultations?token={access_token}",
        json={
            "doctor_name": "Dr. Helen Cho",
            "clinic_name": "Avenger Medical Facility",
            "chief_complaint": "Shoulder strain from archery training",
            "clinical_observations": "Full range of motion, mild supraspinatus tenderness.",
            "recommended_actions": "Physical therapy 3x/week, cold compress for 15 mins daily."
        }, headers=doctor_headers
    )
    assert consult_resp.status_code == 201
    assert consult_resp.json()["data"]["doctor_name"] == "Dr. Helen Cho"

    consult_list = await client.get(
        f"/api/v1/doctor/patient/{patient_id}/consultations?token={access_token}",
        headers=doctor_headers,
    )
    assert consult_list.status_code == 200

    # 5. Patient Checks Timeline for Doctor Consultation Event
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    t_events = timeline_resp.json()["data"]["events"]
    assert any("Doctor Consultation" in e["title"] for e in t_events)

    access_logs = await client.get("/api/v1/privacy/access-logs", headers=headers)
    assert access_logs.status_code == 200
    assert any(row["action"] == "DOCTOR_VIEW" for row in access_logs.json()["data"])

    # 6. Patient Revokes Access Grant (Kill-switch)
    revoke_resp = await client.post(f"/api/v1/sharing/grants/{grant_id}/revoke", headers=headers)
    assert revoke_resp.status_code == 200

    # 7. Doctor Subsequent Access Attempt Must Be Forbidden
    denied_resp = await client.get(f"/api/v1/doctor/patient/{patient_id}/summary?token={access_token}", headers=doctor_headers)
    assert denied_resp.status_code == 403
