import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.nutrition.schemas import (
    FoodItemResponse,
    MealLogCreateRequest,
    MealLogResponse,
    MealLogItemResponse,
    DailyNutritionSummaryResponse,
    WeeklyNutritionTrendResponse,
    NutritionTargetRequest,
    NutritionTargetResponse,
    GenerateMealPlanRequest,
    MealPlanResponse,
    GroceryListResponse,
    GroceryItemResponse,
)
from app.modules.nutrition.service import NutritionService

router = APIRouter(prefix="/nutrition", tags=["Nutrition & Meal Tracking"])

@router.get("/foods/search", response_model=ApiResponse[List[FoodItemResponse]], status_code=status.HTTP_200_OK)
async def search_foods(
    query: Optional[str] = Query(None, description="Search keyword for food item"),
    category: Optional[str] = Query(None, description="Food category filter"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[FoodItemResponse]]:
    """Search reference food nutritional database with calories, protein, carbs, fat, and fiber."""
    service = NutritionService(db)
    foods = await service.search_foods(query=query, category=category)
    payload = [FoodItemResponse.model_validate(f) for f in foods]
    return ApiResponse[List[FoodItemResponse]](success=True, message="Foods retrieved", data=payload)

@router.post("/meals", response_model=ApiResponse[MealLogResponse], status_code=status.HTTP_201_CREATED)
async def log_meal(
    req: MealLogCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MealLogResponse]:
    """Log a meal entry (Breakfast, Lunch, Dinner, Snack) with automatic macronutrient summation."""
    service = NutritionService(db)
    meal = await service.log_meal(current_user.id, req)
    
    payload = MealLogResponse(
        id=meal.id,
        user_id=meal.user_id,
        meal_type=meal.meal_type.value,
        logged_date=meal.logged_date,
        total_calories=meal.total_calories,
        total_protein=meal.total_protein,
        total_carbs=meal.total_carbs,
        total_fat=meal.total_fat,
        notes=meal.notes,
        items=[
            MealLogItemResponse(
                id=i.id,
                food_name=i.food_name,
                serving_quantity=i.serving_quantity,
                serving_unit=i.serving_unit,
                calories_kcal=i.calories_kcal,
                protein_g=i.protein_g,
                carbs_g=i.carbs_g,
                fat_g=i.fat_g,
            )
            for i in meal.items
        ],
        created_at=meal.created_at,
    )
    return ApiResponse[MealLogResponse](success=True, message="Meal logged successfully", data=payload)

@router.get("/daily-summary", response_model=ApiResponse[DailyNutritionSummaryResponse], status_code=status.HTTP_200_OK)
async def get_daily_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[DailyNutritionSummaryResponse]:
    """Retrieve today's calories and macros consumed versus daily target budget."""
    service = NutritionService(db)
    summary = await service.get_daily_summary(current_user.id)
    return ApiResponse[DailyNutritionSummaryResponse](success=True, message="Daily summary retrieved", data=summary)

@router.get("/weekly-trends", response_model=ApiResponse[WeeklyNutritionTrendResponse], status_code=status.HTTP_200_OK)
async def get_weekly_trends(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[WeeklyNutritionTrendResponse]:
    """Retrieve 7-day nutritional trends and daily average macronutrients for charting."""
    service = NutritionService(db)
    trends = await service.get_weekly_trends(current_user.id)
    return ApiResponse[WeeklyNutritionTrendResponse](success=True, message="Weekly trends retrieved", data=trends)

@router.get("/targets", response_model=ApiResponse[NutritionTargetResponse], status_code=status.HTTP_200_OK)
async def get_nutrition_targets(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NutritionTargetResponse]:
    """Get personalized daily nutrition and hydration targets."""
    service = NutritionService(db)
    target = await service.get_or_create_targets(current_user.id)
    payload = NutritionTargetResponse.model_validate(target)
    return ApiResponse[NutritionTargetResponse](success=True, message="Nutrition targets retrieved", data=payload)

@router.put("/targets", response_model=ApiResponse[NutritionTargetResponse], status_code=status.HTTP_200_OK)
async def update_nutrition_targets(
    req: NutritionTargetRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[NutritionTargetResponse]:
    """Update personalized daily nutrition and hydration targets."""
    service = NutritionService(db)
    target = await service.update_targets(current_user.id, req)
    payload = NutritionTargetResponse.model_validate(target)
    return ApiResponse[NutritionTargetResponse](success=True, message="Nutrition targets updated", data=payload)

@router.post("/meal-planner/generate", response_model=ApiResponse[MealPlanResponse], status_code=status.HTTP_201_CREATED)
async def generate_meal_plan(
    req: GenerateMealPlanRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MealPlanResponse]:
    """Generate structured AI day meal suggestions matching user goals, diet, and regional cuisine."""
    service = NutritionService(db)
    plan = await service.generate_ai_meal_plan(current_user.id, req)
    payload = MealPlanResponse(
        id=plan.id,
        user_id=plan.user_id,
        title=plan.title,
        goal=plan.goal,
        diet_type=plan.diet_type.value,
        cuisine_preference=plan.cuisine_preference,
        target_calories=plan.target_calories,
        plan_data=plan.plan_data,
        created_at=plan.created_at,
    )
    return ApiResponse[MealPlanResponse](success=True, message="Meal plan generated successfully", data=payload)

@router.post("/meal-planner/{plan_id}/grocery-list", response_model=ApiResponse[GroceryListResponse], status_code=status.HTTP_201_CREATED)
async def generate_grocery_list(
    plan_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GroceryListResponse]:
    """Derive categorized grocery shopping checklist from a selected meal plan."""
    service = NutritionService(db)
    grocery = await service.generate_grocery_list_from_plan(current_user.id, plan_id)
    payload = GroceryListResponse(
        id=grocery.id,
        user_id=grocery.user_id,
        meal_plan_id=grocery.meal_plan_id,
        title=grocery.title,
        items_data=[GroceryItemResponse(**i) for i in grocery.items_data],
        is_completed=grocery.is_completed,
        created_at=grocery.created_at,
    )
    return ApiResponse[GroceryListResponse](success=True, message="Grocery list generated", data=payload)

@router.get("/grocery-lists", response_model=ApiResponse[List[GroceryListResponse]], status_code=status.HTTP_200_OK)
async def list_grocery_lists(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[GroceryListResponse]]:
    """List saved grocery checklists."""
    service = NutritionService(db)
    lists = await service.get_grocery_lists(current_user.id)
    payload = [
        GroceryListResponse(
            id=g.id,
            user_id=g.user_id,
            meal_plan_id=g.meal_plan_id,
            title=g.title,
            items_data=[GroceryItemResponse(**i) for i in g.items_data],
            is_completed=g.is_completed,
            created_at=g.created_at,
        )
        for g in lists
    ]
    return ApiResponse[List[GroceryListResponse]](success=True, message="Grocery lists retrieved", data=payload)
