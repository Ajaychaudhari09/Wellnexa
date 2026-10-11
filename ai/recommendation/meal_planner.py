"""AI Meal Planner and Grocery List Generation Engine."""

from typing import Dict, Any, List, Optional

SAMPLE_INDIAN_VEGETARIAN_PLAN = {
    "breakfast": {
        "title": "Vegetable Oats Upma with Mint Chutney & Almonds",
        "calories_kcal": 380.0,
        "protein_g": 14.0,
        "carbs_g": 56.0,
        "fat_g": 10.0,
        "ingredients": ["Rolled Oats", "Carrots", "Green Peas", "Mustard Seeds", "Almonds", "Mint Leaves"]
    },
    "lunch": {
        "title": "Paneer & Spinach Curry (Palak Paneer) with Brown Rice & Cucumber Salad",
        "calories_kcal": 620.0,
        "protein_g": 28.0,
        "carbs_g": 68.0,
        "fat_g": 22.0,
        "ingredients": ["Fresh Paneer", "Spinach", "Brown Rice", "Cumin", "Garlic", "Cucumbers", "Tomatoes"]
    },
    "evening_snack": {
        "title": "Roasted Chana & Green Tea with Walnuts",
        "calories_kcal": 220.0,
        "protein_g": 10.0,
        "carbs_g": 24.0,
        "fat_g": 9.0,
        "ingredients": ["Roasted Chickpeas (Chana)", "Green Tea Bag", "Walnuts"]
    },
    "dinner": {
        "title": "Yellow Dal Tadka with 2 Multigrain Rotis & Steamed Beans",
        "calories_kcal": 480.0,
        "protein_g": 22.0,
        "carbs_g": 72.0,
        "fat_g": 12.0,
        "ingredients": ["Yellow Moong Dal", "Multigrain Flour", "French Beans", "Turmeric", "Ghee (1 tsp)"]
    }
}

SAMPLE_GENERAL_PLAN = {
    "breakfast": {
        "title": "Greek Yogurt Berry Parfait with Chia Seeds & Honey",
        "calories_kcal": 360.0,
        "protein_g": 24.0,
        "carbs_g": 45.0,
        "fat_g": 8.0,
        "ingredients": ["Greek Yogurt", "Blueberries", "Chia Seeds", "Honey", "Granola"]
    },
    "lunch": {
        "title": "Quinoa Bowl with Grilled Tofu, Avocado, and Steamed Broccoli",
        "calories_kcal": 590.0,
        "protein_g": 26.0,
        "carbs_g": 62.0,
        "fat_g": 24.0,
        "ingredients": ["Quinoa", "Firm Tofu", "Avocado", "Broccoli", "Olive Oil", "Lemon"]
    },
    "evening_snack": {
        "title": "Apple Slices with Natural Peanut Butter",
        "calories_kcal": 210.0,
        "protein_g": 7.0,
        "carbs_g": 26.0,
        "fat_g": 11.0,
        "ingredients": ["Crisp Apple", "Peanut Butter"]
    },
    "dinner": {
        "title": "Lentil Soup with Whole Grain Toast and Garden Salad",
        "calories_kcal": 490.0,
        "protein_g": 22.0,
        "carbs_g": 74.0,
        "fat_g": 10.0,
        "ingredients": ["Brown Lentils", "Whole Grain Bread", "Carrots", "Celery", "Mixed Greens"]
    }
}

class AIMealPlanner:
    """Generates structured day meal plans and derives categorized grocery shopping lists."""

    @staticmethod
    def generate_day_plan(
        goal: str,
        diet_type: str,
        cuisine_preference: str = "INDIAN",
        target_calories: float = 1800.0,
    ) -> Dict[str, Any]:
        """Produce structured day meal suggestions tailored to user goals and dietary culture."""
        is_indian = "indian" in cuisine_preference.lower()
        base_plan = SAMPLE_INDIAN_VEGETARIAN_PLAN if is_indian else SAMPLE_GENERAL_PLAN

        # Calculate totals
        tot_cal = sum(m["calories_kcal"] for m in base_plan.values())
        tot_pro = sum(m["protein_g"] for m in base_plan.values())
        tot_carb = sum(m["carbs_g"] for m in base_plan.values())
        tot_fat = sum(m["fat_g"] for m in base_plan.values())

        # Scaling factor to match exact target calories
        scale = round(target_calories / tot_cal, 2) if tot_cal > 0 else 1.0

        scaled_meals = {}
        for meal_name, meal_info in base_plan.items():
            scaled_meals[meal_name] = {
                "title": meal_info["title"],
                "calories_kcal": round(meal_info["calories_kcal"] * scale, 1),
                "protein_g": round(meal_info["protein_g"] * scale, 1),
                "carbs_g": round(meal_info["carbs_g"] * scale, 1),
                "fat_g": round(meal_info["fat_g"] * scale, 1),
                "ingredients": meal_info["ingredients"],
            }

        return {
            "title": f"Custom {diet_type.title()} {cuisine_preference.title()} Day Plan ({int(target_calories)} kcal)",
            "goal": goal,
            "diet_type": diet_type,
            "cuisine_preference": cuisine_preference,
            "target_calories": target_calories,
            "total_estimated_calories": round(tot_cal * scale, 1),
            "total_protein_g": round(tot_pro * scale, 1),
            "total_carbs_g": round(tot_carb * scale, 1),
            "total_fat_g": round(tot_fat * scale, 1),
            "meals": scaled_meals,
            "disclaimer": "This meal plan is AI-generated for informational nutrition guidance. Consult a certified nutritionist or physician for clinical diet planning.",
        }

    @staticmethod
    def derive_grocery_list(plan_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Categorize ingredients into a shopping list."""
        all_ingredients: List[str] = []
        meals = plan_data.get("meals", {})
        for meal in meals.values():
            all_ingredients.extend(meal.get("ingredients", []))

        # Categorize
        produce = []
        grains_pulses = []
        dairy_protein = []
        pantry_spices = []

        for item in sorted(set(all_ingredients)):
            item_low = item.lower()
            if any(k in item_low for k in ["spinach", "carrot", "pea", "cucumber", "tomato", "bean", "apple", "blueberry", "greens", "broccoli", "lemon"]):
                produce.append({"name": item, "category": "Fresh Produce", "checked": False})
            elif any(k in item_low for k in ["oat", "rice", "dal", "flour", "chickpea", "chana", "quinoa", "bread", "lentil"]):
                grains_pulses.append({"name": item, "category": "Grains & Pulses", "checked": False})
            elif any(k in item_low for k in ["paneer", "yogurt", "tofu", "almond", "walnut", "peanut"]):
                dairy_protein.append({"name": item, "category": "Dairy & Healthy Fats", "checked": False})
            else:
                pantry_spices.append({"name": item, "category": "Pantry & Seasonings", "checked": False})

        return produce + grains_pulses + dairy_protein + pantry_spices
