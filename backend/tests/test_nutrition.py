import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_nutrition_search_meal_logging_and_ai_planner(client: AsyncClient):
    # 1. Register & Login
    await client.post("/api/v1/auth/register", json={
        "email": "nutrition_user@example.com",
        "password": "Password123!",
        "first_name": "Thor",
        "last_name": "Odinson"
    })
    login_resp = await client.post("/api/v1/auth/login", json={
        "email": "nutrition_user@example.com",
        "password": "Password123!"
    })
    token = login_resp.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Search Food Database
    search_resp = await client.get("/api/v1/nutrition/foods/search?query=Oats", headers=headers)
    assert search_resp.status_code == 200
    foods = search_resp.json()["data"]
    assert len(foods) >= 1
    assert "Oats" in foods[0]["name"]

    # 3. Configure Nutrition Targets (2500 kcal, 150g protein)
    target_resp = await client.put("/api/v1/nutrition/targets", json={
        "calorie_target_kcal": 2500.0,
        "protein_target_g": 150.0,
        "carbs_target_g": 300.0,
        "fat_target_g": 75.0,
        "water_target_liters": 3.5
    }, headers=headers)
    assert target_resp.status_code == 200
    assert target_resp.json()["data"]["calorie_target_kcal"] == 2500.0

    # 4. Log a Meal (Breakfast: Oats + Greek Yogurt)
    meal_payload = {
        "meal_type": "BREAKFAST",
        "notes": "Post-workout morning fuel",
        "items": [
            {
                "food_name": "Rolled Oats",
                "serving_quantity": 2.0,
                "serving_unit": "servings (80g)",
                "calories_kcal": 300.0,
                "protein_g": 10.0,
                "carbs_g": 54.0,
                "fat_g": 5.0
            },
            {
                "food_name": "Greek Yogurt",
                "serving_quantity": 1.0,
                "serving_unit": "cup",
                "calories_kcal": 130.0,
                "protein_g": 18.0,
                "carbs_g": 6.0,
                "fat_g": 1.0
            }
        ]
    }
    meal_resp = await client.post("/api/v1/nutrition/meals", json=meal_payload, headers=headers)
    assert meal_resp.status_code == 201
    meal_data = meal_resp.json()["data"]
    assert meal_data["total_calories"] == 430.0
    assert meal_data["total_protein"] == 28.0

    # 5. Check Daily Summary
    daily_resp = await client.get("/api/v1/nutrition/daily-summary", headers=headers)
    assert daily_resp.status_code == 200
    daily_data = daily_resp.json()["data"]
    assert daily_data["total_calories"] == 430.0
    assert daily_data["remaining_calories"] == 2070.0 # 2500 - 430 = 2070
    assert daily_data["meals_logged_count"] == 1

    # 6. Test AI Meal Planner Generation (Indian Vegetarian Plan)
    planner_payload = {
        "goal": "MUSCLE_GAIN",
        "diet_type": "VEGETARIAN",
        "cuisine_preference": "INDIAN",
        "target_calories": 2200.0
    }
    plan_resp = await client.post("/api/v1/nutrition/meal-planner/generate", json=planner_payload, headers=headers)
    assert plan_resp.status_code == 201
    plan_data = plan_resp.json()["data"]
    plan_id = plan_data["id"]
    assert "Indian" in plan_data["title"]
    assert plan_data["target_calories"] == 2200.0
    assert "breakfast" in plan_data["plan_data"]["meals"]

    # 7. Derive Grocery List from Meal Plan
    grocery_resp = await client.post(f"/api/v1/nutrition/meal-planner/{plan_id}/grocery-list", headers=headers)
    assert grocery_resp.status_code == 201
    grocery_data = grocery_resp.json()["data"]
    assert len(grocery_data["items_data"]) >= 5
    categories = {i["category"] for i in grocery_data["items_data"]}
    assert "Fresh Produce" in categories or "Grains & Pulses" in categories

    # 8. Check Timeline for Meal Logged & Plan Generated events
    timeline_resp = await client.get("/api/v1/timeline", headers=headers)
    assert timeline_resp.status_code == 200
    t_events = timeline_resp.json()["data"]["events"]
    assert any("Breakfast Logged" in e["title"] for e in t_events)
    assert any("Meal Plan Generated" in e["title"] for e in t_events)
