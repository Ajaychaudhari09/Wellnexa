import uuid
from datetime import datetime, date, timedelta, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func

from app.core.exceptions import NotFoundException, WellNexaException
from app.models.nutrition import (
    FoodItem,
    MealLog,
    MealLogItem,
    NutritionTarget,
    MealPlan,
    GroceryList,
    MealTypeEnum,
    DietTypeEnum,
)
from app.models.timeline import TimelineCategoryEnum, TimelineEventTypeEnum
from app.models.audit import AuditLog
from ai.recommendation.meal_planner import AIMealPlanner
from app.modules.timeline.service import TimelineService
from app.modules.nutrition.schemas import (
    MealLogCreateRequest,
    NutritionTargetRequest,
    GenerateMealPlanRequest,
    DailyNutritionSummaryResponse,
    WeeklyNutritionTrendResponse,
    DayTrendItem,
    MealLogResponse,
    MealLogItemResponse,
    GroceryItemResponse,
)

INITIAL_REFERENCE_FOODS = [
    {"name": "Rolled Oats", "serving_size": 40.0, "serving_unit": "g", "calories_kcal": 150.0, "protein_g": 5.0, "carbs_g": 27.0, "fat_g": 2.5, "fiber_g": 4.0, "category": "Grains"},
    {"name": "Paneer (Cottage Cheese)", "serving_size": 100.0, "serving_unit": "g", "calories_kcal": 265.0, "protein_g": 18.0, "carbs_g": 3.0, "fat_g": 20.0, "fiber_g": 0.0, "category": "Dairy"},
    {"name": "Brown Rice (Cooked)", "serving_size": 150.0, "serving_unit": "g", "calories_kcal": 165.0, "protein_g": 3.5, "carbs_g": 35.0, "fat_g": 1.2, "fiber_g": 2.5, "category": "Grains"},
    {"name": "Yellow Moong Dal (Cooked)", "serving_size": 150.0, "serving_unit": "g", "calories_kcal": 140.0, "protein_g": 9.0, "carbs_g": 24.0, "fat_g": 1.0, "fiber_g": 4.0, "category": "Pulses"},
    {"name": "Whole Wheat Roti / Chapati", "serving_size": 1.0, "serving_unit": "piece", "calories_kcal": 85.0, "protein_g": 3.0, "carbs_g": 17.0, "fat_g": 0.5, "fiber_g": 2.5, "category": "Grains"},
    {"name": "Greek Yogurt (Plain)", "serving_size": 150.0, "serving_unit": "g", "calories_kcal": 100.0, "protein_g": 15.0, "carbs_g": 6.0, "fat_g": 0.5, "fiber_g": 0.0, "category": "Dairy"},
    {"name": "Boiled Egg", "serving_size": 1.0, "serving_unit": "large", "calories_kcal": 78.0, "protein_g": 6.3, "carbs_g": 0.6, "fat_g": 5.3, "fiber_g": 0.0, "category": "Protein"},
    {"name": "Grilled Chicken Breast", "serving_size": 100.0, "serving_unit": "g", "calories_kcal": 165.0, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6, "fiber_g": 0.0, "category": "Meat"},
    {"name": "Apple", "serving_size": 1.0, "serving_unit": "medium", "calories_kcal": 95.0, "protein_g": 0.5, "carbs_g": 25.0, "fat_g": 0.3, "fiber_g": 4.4, "category": "Fruits"},
    {"name": "Almonds", "serving_size": 30.0, "serving_unit": "g", "calories_kcal": 170.0, "protein_g": 6.0, "carbs_g": 6.0, "fat_g": 15.0, "fiber_g": 3.5, "category": "Nuts & Seeds"},
]

class NutritionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.timeline_service = TimelineService(db)

    # ----------------- Foods & Search -----------------
    async def seed_initial_foods_if_empty(self) -> None:
        count_q = select(func.count()).select_from(FoodItem)
        count_res = await self.db.execute(count_q)
        if (count_res.scalar() or 0) == 0:
            for item in INITIAL_REFERENCE_FOODS:
                food = FoodItem(**item, is_custom=False)
                self.db.add(food)
            await self.db.flush()

    async def search_foods(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 30) -> List[FoodItem]:
        await self.seed_initial_foods_if_empty()
        q = select(FoodItem)
        if query:
            q = q.where(FoodItem.name.ilike(f"%{query.strip()}%"))
        if category:
            q = q.where(FoodItem.category == category)
        q = q.limit(limit)
        result = await self.db.execute(q)
        return list(result.scalars().all())

    # ----------------- Meal Logging -----------------
    async def log_meal(self, user_id: uuid.UUID, req: MealLogCreateRequest) -> MealLog:
        logged_date = req.logged_date or datetime.now(timezone.utc).date()

        tot_cal = sum(i.calories_kcal for i in req.items)
        tot_pro = sum(i.protein_g for i in req.items)
        tot_carb = sum(i.carbs_g for i in req.items)
        tot_fat = sum(i.fat_g for i in req.items)

        meal = MealLog(
            user_id=user_id,
            meal_type=req.meal_type,
            logged_date=logged_date,
            total_calories=round(tot_cal, 1),
            total_protein=round(tot_pro, 1),
            total_carbs=round(tot_carb, 1),
            total_fat=round(tot_fat, 1),
            notes=req.notes.strip() if req.notes else None,
        )
        self.db.add(meal)
        await self.db.flush()

        for item in req.items:
            log_item = MealLogItem(
                meal_log_id=meal.id,
                food_item_id=item.food_item_id,
                food_name=item.food_name.strip(),
                serving_quantity=item.serving_quantity,
                serving_unit=item.serving_unit,
                calories_kcal=item.calories_kcal,
                protein_g=item.protein_g,
                carbs_g=item.carbs_g,
                fat_g=item.fat_g,
            )
            self.db.add(log_item)

        await self.db.flush()

        # Emit timeline event
        m_title = req.meal_type.value.replace("_", " ").title()
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.WELLNESS,
            event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
            title=f"{m_title} Logged",
            summary=f"Logged {len(req.items)} items • {round(tot_cal, 1)} kcal (P: {round(tot_pro, 1)}g, C: {round(tot_carb, 1)}g, F: {round(tot_fat, 1)}g)",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(meal.id),
            reference_type="meal_log",
        )

        q = select(MealLog).where(MealLog.id == meal.id)
        res = await self.db.execute(q)
        return res.scalar_one()

    # ----------------- Targets -----------------
    async def get_or_create_targets(self, user_id: uuid.UUID) -> NutritionTarget:
        query = select(NutritionTarget).where(NutritionTarget.user_id == user_id)
        result = await self.db.execute(query)
        target = result.scalar_one_or_none()
        if not target:
            target = NutritionTarget(user_id=user_id)
            self.db.add(target)
            await self.db.flush()
        return target

    async def update_targets(self, user_id: uuid.UUID, req: NutritionTargetRequest) -> NutritionTarget:
        target = await self.get_or_create_targets(user_id)
        target.calorie_target_kcal = req.calorie_target_kcal
        target.protein_target_g = req.protein_target_g
        target.carbs_target_g = req.carbs_target_g
        target.fat_target_g = req.fat_target_g
        target.water_target_liters = req.water_target_liters
        await self.db.flush()
        return target

    # ----------------- Daily Summary -----------------
    async def get_daily_summary(self, user_id: uuid.UUID, target_date: Optional[date] = None) -> DailyNutritionSummaryResponse:
        t_date = target_date or datetime.now(timezone.utc).date()
        target = await self.get_or_create_targets(user_id)

        query = select(MealLog).where(
            and_(MealLog.user_id == user_id, MealLog.logged_date == t_date)
        ).order_by(MealLog.created_at.asc())
        result = await self.db.execute(query)
        meals = list(result.scalars().all())

        tot_cal = sum(m.total_calories for m in meals)
        tot_pro = sum(m.total_protein for m in meals)
        tot_carb = sum(m.total_carbs for m in meals)
        tot_fat = sum(m.total_fat for m in meals)

        meal_responses = [
            MealLogResponse(
                id=m.id,
                user_id=m.user_id,
                meal_type=m.meal_type.value,
                logged_date=m.logged_date,
                total_calories=m.total_calories,
                total_protein=m.total_protein,
                total_carbs=m.total_carbs,
                total_fat=m.total_fat,
                notes=m.notes,
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
                    for i in m.items
                ],
                created_at=m.created_at,
            )
            for m in meals
        ]

        return DailyNutritionSummaryResponse(
            date=t_date,
            total_calories=round(tot_cal, 1),
            calorie_target=target.calorie_target_kcal,
            remaining_calories=round(max(0.0, target.calorie_target_kcal - tot_cal), 1),
            total_protein=round(tot_pro, 1),
            protein_target=target.protein_target_g,
            total_carbs=round(tot_carb, 1),
            carbs_target=target.carbs_target_g,
            total_fat=round(tot_fat, 1),
            fat_target=target.fat_target_g,
            meals_logged_count=len(meals),
            meals=meal_responses,
        )

    # ----------------- Weekly Trends -----------------
    async def get_weekly_trends(self, user_id: uuid.UUID) -> WeeklyNutritionTrendResponse:
        today = datetime.now(timezone.utc).date()
        history: List[DayTrendItem] = []

        for i in range(6, -1, -1):
            d = today - timedelta(days=i)
            q = select(MealLog).where(
                and_(MealLog.user_id == user_id, MealLog.logged_date == d)
            )
            res = await self.db.execute(q)
            day_meals = list(res.scalars().all())

            cals = sum(m.total_calories for m in day_meals)
            pro = sum(m.total_protein for m in day_meals)
            carb = sum(m.total_carbs for m in day_meals)
            fat = sum(m.total_fat for m in day_meals)

            history.append(
                DayTrendItem(
                    date=d,
                    day_name=d.strftime("%a"),
                    calories=round(cals, 1),
                    protein_g=round(pro, 1),
                    carbs_g=round(carb, 1),
                    fat_g=round(fat, 1),
                )
            )

        active_days = [h for h in history if h.calories > 0]
        avg_cal = round(sum(h.calories for h in history) / 7.0, 1)
        avg_pro = round(sum(h.protein_g for h in history) / 7.0, 1)
        avg_carb = round(sum(h.carbs_g for h in history) / 7.0, 1)
        avg_fat = round(sum(h.fat_g for h in history) / 7.0, 1)

        return WeeklyNutritionTrendResponse(
            average_daily_calories=avg_cal,
            average_protein_g=avg_pro,
            average_carbs_g=avg_carb,
            average_fat_g=avg_fat,
            history=history,
        )

    # ----------------- AI Meal Planner -----------------
    async def generate_ai_meal_plan(self, user_id: uuid.UUID, req: GenerateMealPlanRequest) -> MealPlan:
        plan_dict = AIMealPlanner.generate_day_plan(
            goal=req.goal,
            diet_type=req.diet_type.value,
            cuisine_preference=req.cuisine_preference,
            target_calories=req.target_calories,
        )

        meal_plan = MealPlan(
            user_id=user_id,
            title=plan_dict["title"],
            goal=req.goal,
            diet_type=req.diet_type,
            cuisine_preference=req.cuisine_preference,
            target_calories=req.target_calories,
            plan_data=plan_dict,
        )
        self.db.add(meal_plan)
        await self.db.flush()

        # Emit timeline event
        await self.timeline_service.record_event(
            user_id=user_id,
            category=TimelineCategoryEnum.WELLNESS,
            event_type=TimelineEventTypeEnum.SYSTEM_NOTICE,
            title="AI Meal Plan Generated",
            summary=f"{plan_dict['title']} created with target {req.target_calories} kcal.",
            occurred_at=datetime.now(timezone.utc),
            reference_id=str(meal_plan.id),
            reference_type="meal_plan",
        )

        return meal_plan

    # ----------------- Grocery List -----------------
    async def generate_grocery_list_from_plan(self, user_id: uuid.UUID, meal_plan_id: uuid.UUID) -> GroceryList:
        query = select(MealPlan).where(
            and_(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
        )
        result = await self.db.execute(query)
        plan = result.scalar_one_or_none()
        if not plan:
            raise NotFoundException("MealPlan", meal_plan_id)

        items = AIMealPlanner.derive_grocery_list(plan.plan_data)

        grocery = GroceryList(
            user_id=user_id,
            meal_plan_id=plan.id,
            title=f"Grocery List for {plan.title}",
            items_data=items,
            is_completed=False,
        )
        self.db.add(grocery)
        await self.db.flush()
        return grocery

    async def get_grocery_lists(self, user_id: uuid.UUID) -> List[GroceryList]:
        query = select(GroceryList).where(GroceryList.user_id == user_id).order_by(desc(GroceryList.created_at))
        result = await self.db.execute(query)
        return list(result.scalars().all())
