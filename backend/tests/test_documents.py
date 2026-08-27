import io
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_document_upload_download_and_lifecycle(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "doc_user@example.com",
        "password": "Password123!",
        "first_name": "Stephen",
        "last_name": "Strange"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "doc_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload a sample mock PDF report
    pdf_content = b"%PDF-1.4 Mock Medical Blood Report Hemoglobin 14.2 g/dL Glucose 95 mg/dL"
    files = {
        "file": ("blood_test_report.pdf", io.BytesIO(pdf_content), "application/pdf")
    }
    data = {
        "category": "MEDICAL_REPORT",
        "title": "Complete Blood Count & Fasting Glucose",
        "notes": "Routine annual health checkup"
    }

    upload_resp = await client.post("/api/v1/documents/upload", headers=headers, files=files, data=data)
    assert upload_resp.status_code == 201
    doc_data = upload_resp.json()["data"]
    doc_id = doc_data["id"]
    assert doc_data["title"] == "Complete Blood Count & Fasting Glucose"
    assert doc_data["category"] == "MEDICAL_REPORT"
    assert doc_data["mime_type"] == "application/pdf"
    assert doc_data["file_size_bytes"] == len(pdf_content)

    # 3. Retrieve document metadata
    meta_resp = await client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert meta_resp.status_code == 200
    assert meta_resp.json()["data"]["id"] == doc_id

    # 4. Download file
    dl_resp = await client.get(f"/api/v1/documents/{doc_id}/download", headers=headers)
    assert dl_resp.status_code == 200
    assert dl_resp.content == pdf_content

    # 5. Check Timeline to verify auto-generation of timeline event
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    events = timeline_resp.json()["data"]["events"]
    assert any("Report Uploaded" in e["title"] or "Medical Report Uploaded" in e["title"] for e in events)

    # 6. Delete document
    del_resp = await client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert del_resp.status_code == 200

    # 7. Verify document is removed
    get_after_del = await client.get(f"/api/v1/documents/{doc_id}", headers=headers)
    assert get_after_del.status_code == 404

@pytest.mark.asyncio
async def test_invalid_mime_type_rejected(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "invalid_mime_user@example.com",
        "password": "Password123!",
        "first_name": "Test",
        "last_name": "User"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "invalid_mime_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Upload invalid file (.exe / text/plain)
    fake_exe = b"MZ\x90\x00executable binary content"
    files = {
        "file": ("malicious.exe", io.BytesIO(fake_exe), "application/x-msdownload")
    }
    upload_resp = await client.post("/api/v1/documents/upload", headers=headers, files=files, data={"category": "OTHER"})
    assert upload_resp.status_code == 400
