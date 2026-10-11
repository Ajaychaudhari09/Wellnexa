import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.nutrition import MealTypeEnum, DietTypeEnum

# ----------------- Foods -----------------
class FoodItemResponse(BaseModel):
    id: uuid.UUID
    name: str
    serving_size: float
    serving_unit: str
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    category: Optional[str] = None
    is_custom: bool

    class Config:
        from_attributes = True

# ----------------- Meal Logging -----------------
class MealLogItemCreate(BaseModel):
    food_item_id: Optional[uuid.UUID] = None
    food_name: str = Field(..., min_length=1, max_length=150)
    serving_quantity: float = Field(default=1.0, gt=0)
    serving_unit: str = Field(default="serving")
    calories_kcal: float = Field(..., ge=0)
    protein_g: float = Field(default=0.0, ge=0)
    carbs_g: float = Field(default=0.0, ge=0)
    fat_g: float = Field(default=0.0, ge=0)

class MealLogCreateRequest(BaseModel):
    meal_type: MealTypeEnum = MealTypeEnum.BREAKFAST
    logged_date: Optional[date] = None
    items: List[MealLogItemCreate]
    notes: Optional[str] = None

class MealLogItemResponse(BaseModel):
    id: uuid.UUID
    food_name: str
    serving_quantity: float
    serving_unit: str
    calories_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float

    class Config:
        from_attributes = True

class MealLogResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    meal_type: str
    logged_date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    notes: Optional[str] = None
    items: List[MealLogItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------- Daily & Weekly Summaries -----------------
class DailyNutritionSummaryResponse(BaseModel):
    date: date
    total_calories: float
    calorie_target: float
    remaining_calories: float
    total_protein: float
    protein_target: float
    total_carbs: float
    carbs_target: float
    total_fat: float
    fat_target: float
    meals_logged_count: int
    meals: List[MealLogResponse]

class DayTrendItem(BaseModel):
    date: date
    day_name: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float

class WeeklyNutritionTrendResponse(BaseModel):
    average_daily_calories: float
    average_protein_g: float
    average_carbs_g: float
    average_fat_g: float
    history: List[DayTrendItem]

# ----------------- Targets -----------------
class NutritionTargetRequest(BaseModel):
    calorie_target_kcal: float = Field(..., gt=500, le=8000)
    protein_target_g: float = Field(default=75.0, ge=0)
    carbs_target_g: float = Field(default=250.0, ge=0)
    fat_target_g: float = Field(default=65.0, ge=0)
    water_target_liters: float = Field(default=2.5, ge=0.5)

class NutritionTargetResponse(BaseModel):
    user_id: uuid.UUID
    calorie_target_kcal: float
    protein_target_g: float
    carbs_target_g: float
    fat_target_g: float
    water_target_liters: float

    class Config:
        from_attributes = True

# ----------------- AI Meal Planner & Grocery -----------------
class GenerateMealPlanRequest(BaseModel):
    goal: str = Field(default="WEIGHT_MANAGEMENT", description="e.g. WEIGHT_LOSS, MUSCLE_GAIN, BLOOD_SUGAR_CONTROL")
    diet_type: DietTypeEnum = DietTypeEnum.VEGETARIAN
    cuisine_preference: str = Field(default="INDIAN", description="e.g. INDIAN, MEDITERRANEAN, CONTINENTAL")
    target_calories: float = Field(default=1800.0, gt=800, le=6000)

class MealPlanResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    goal: str
    diet_type: str
    cuisine_preference: str
    target_calories: float
    plan_data: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

class GroceryItemResponse(BaseModel):
    name: str
    category: str
    checked: bool

class GroceryListResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    meal_plan_id: Optional[uuid.UUID] = None
    title: str
    items_data: List[GroceryItemResponse]
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True
