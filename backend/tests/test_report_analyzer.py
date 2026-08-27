import io
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_report_explanation_and_historical_comparison(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "analysis_user@example.com",
        "password": "Password123!",
        "first_name": "Natasha",
        "last_name": "Romanoff"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "analysis_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload & Confirm Report 1 (Past Report - January: Hemoglobin 11.5, Fasting Glucose 90)
    report1_text = (
        "CBC REPORT - JANUARY\n"
        "Hemoglobin: 11.5 g/dL\n"
        "Fasting Blood Sugar: 90.0 mg/dL\n"
    ).encode("utf-8")
    up1 = await client.post("/api/v1/documents/upload", headers=headers, files={"file": ("cbc_jan.pdf", io.BytesIO(report1_text), "application/pdf")})
    doc1_id = up1.json()["data"]["id"]
    ocr1 = await client.post(f"/api/v1/reports/process-ocr/{doc1_id}", headers=headers)
    rep1_id = ocr1.json()["data"]["id"]
    rep1_extractions = ocr1.json()["data"]["extractions"]

    # Confirm Report 1
    await client.post(f"/api/v1/reports/{rep1_id}/confirm", json={
        "confirmed_items": [{"extraction_id": e["id"], "confirmed_value": e["detected_value"], "is_confirmed": True} for e in rep1_extractions]
    }, headers=headers)

    # 3. Upload & Confirm Report 2 (Current Report - August: Hemoglobin 13.2, Fasting Glucose 94)
    report2_text = (
        "CBC REPORT - AUGUST\n"
        "Hemoglobin: 13.2 g/dL\n"
        "Fasting Blood Sugar: 94.0 mg/dL\n"
    ).encode("utf-8")
    up2 = await client.post("/api/v1/documents/upload", headers=headers, files={"file": ("cbc_aug.pdf", io.BytesIO(report2_text), "application/pdf")})
    doc2_id = up2.json()["data"]["id"]
    ocr2 = await client.post(f"/api/v1/reports/process-ocr/{doc2_id}", headers=headers)
    rep2_id = ocr2.json()["data"]["id"]
    rep2_extractions = ocr2.json()["data"]["extractions"]

    # Confirm Report 2
    await client.post(f"/api/v1/reports/{rep2_id}/confirm", json={
        "confirmed_items": [{"extraction_id": e["id"], "confirmed_value": e["detected_value"], "is_confirmed": True} for e in rep2_extractions]
    }, headers=headers)

    # 4. Test Plain-Language Explanation
    exp_resp = await client.get(f"/api/v1/reports/{rep2_id}/explanation", headers=headers)
    assert exp_resp.status_code == 200
    exp_data = exp_resp.json()["data"]
    assert exp_data["is_ai_generated"] is True
    assert "medical_disclaimer" in exp_data
    assert len(exp_data["findings"]) >= 2
    assert len(exp_data["suggested_questions_for_doctor"]) >= 2

    # 5. Test Historical Comparison (Report 2 vs Report 1)
    comp_resp = await client.get(f"/api/v1/reports/{rep2_id}/compare", headers=headers)
    assert comp_resp.status_code == 200
    comp_data = comp_resp.json()["data"]
    assert comp_data["has_previous_report"] is True
    assert comp_data["previous_report_id"] == rep1_id

    hb_comp = next(p for p in comp_data["parameters_compared"] if "Hemoglobin" in p["test_name"])
    assert hb_comp["current_value"] == 13.2
    assert hb_comp["previous_value"] == 11.5
    assert hb_comp["delta"] == 1.7 # 13.2 - 11.5 = 1.7
    assert hb_comp["trend_direction"] == "INCREASED"

    # 6. Test Parameter Multi-Report Progression Query
    hist_resp = await client.get("/api/v1/reports/history/Hemoglobin", headers=headers)
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()["data"]
    assert len(hist_data["data_points"]) == 2
    assert hist_data["data_points"][0]["value"] == 11.5
    assert hist_data["data_points"][1]["value"] == 13.2
