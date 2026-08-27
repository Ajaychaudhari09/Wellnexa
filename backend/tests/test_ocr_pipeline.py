import io
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_ocr_pipeline_and_human_confirmation_workflow(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "ocr_patient@example.com",
        "password": "Password123!",
        "first_name": "Peter",
        "last_name": "Parker"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "ocr_patient@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload a Mock CBC & Lipid Laboratory Report Document
    mock_lab_report_text = (
        "METROPOLIS CLINICAL LABORATORIES\n"
        "PATIENT: Peter Parker\n"
        "DATE: 2026-08-20\n\n"
        "COMPLETE BLOOD COUNT (CBC)\n"
        "Hemoglobin: 12.8 g/dL (Ref: 12.0 - 17.5)\n"
        "WBC Count: 7500 cells/mcL (Ref: 4000 - 11000)\n"
        "Platelet Count: 2.8 lakh/mcL (Ref: 1.5 - 4.5)\n\n"
        "LIPID PROFILE\n"
        "Total Cholesterol: 185.0 mg/dL (Ref: 125 - 200)\n"
        "HDL Cholesterol: 48.0 mg/dL (Ref: 40 - 60)\n"
        "Triglycerides: 140.0 mg/dL (Ref: < 150)\n"
        "Fasting Blood Sugar: 92.0 mg/dL (Ref: 70 - 99)\n"
    ).encode("utf-8")

    files = {
        "file": ("lab_report_peter.pdf", io.BytesIO(mock_lab_report_text), "application/pdf")
    }
    data = {
        "category": "MEDICAL_REPORT",
        "title": "Annual Comprehensive Blood & Lipid Panel",
    }
    up_resp = await client.post("/api/v1/documents/upload", headers=headers, files=files, data=data)
    assert up_resp.status_code == 201
    doc_id = up_resp.json()["data"]["id"]

    # 3. Trigger OCR Extraction
    ocr_resp = await client.post(f"/api/v1/reports/process-ocr/{doc_id}", headers=headers)
    assert ocr_resp.status_code == 200
    report_data = ocr_resp.json()["data"]
    report_id = report_data["id"]
    assert report_data["status"] == "PENDING_CONFIRMATION"
    extractions = report_data["extractions"]
    assert len(extractions) >= 5

    # Check extracted values
    hb_item = next(e for e in extractions if "Hemoglobin" in e["test_name"])
    assert hb_item["detected_value"] == 12.8
    assert hb_item["unit"] == "g/dL"
    assert hb_item["flag_status"] == "NORMAL"
    assert hb_item["is_confirmed"] is False

    chol_item = next(e for e in extractions if "Cholesterol" in e["test_name"])
    assert chol_item["detected_value"] == 185.0

    # 4. Confirm Values with Human Correction (Edit Hemoglobin 12.8 -> 13.0)
    confirm_payload = {
        "confirmed_items": [
            {
                "extraction_id": hb_item["id"],
                "confirmed_value": 13.0, # User corrects OCR slightly
                "is_confirmed": True
            },
            {
                "extraction_id": chol_item["id"],
                "confirmed_value": 185.0,
                "is_confirmed": True
            }
        ],
        "lab_name": "Metropolis Clinical Laboratories",
        "notes": "Verified by patient"
    }
    conf_resp = await client.post(f"/api/v1/reports/{report_id}/confirm", json=confirm_payload, headers=headers)
    assert conf_resp.status_code == 200
    conf_data = conf_resp.json()["data"]
    assert conf_data["status"] == "CONFIRMED"

    updated_hb = next(e for e in conf_data["extractions"] if e["id"] == hb_item["id"])
    assert updated_hb["is_confirmed"] is True
    assert updated_hb["confirmed_value"] == 13.0
    assert updated_hb["user_corrected"] is True

    # 5. Verify that confirmed Hemoglobin and Cholesterol are synced to Health Metrics
    metrics_resp = await client.get("/api/v1/metrics", headers=headers)
    assert metrics_resp.status_code == 200
    user_metrics = metrics_resp.json()["data"]
    metric_types = [m["metric_type"] for m in user_metrics]
    assert "HEMOGLOBIN" in metric_types
    assert "CHOLESTEROL_TOTAL" in metric_types

    # 6. Verify Timeline event is emitted
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    t_events = timeline_resp.json()["data"]["events"]
    assert any("Confirmed" in e["title"] for e in t_events)
