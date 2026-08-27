import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.health.schemas import (
    AllergyCreateRequest,
    AllergyResponse,
    ConditionCreateRequest,
    ConditionResponse,
    GoalCreateRequest,
    GoalResponse,
    LifestyleUpdateRequest,
    LifestyleResponse,
    UnifiedHealthSummaryResponse,
)
from app.modules.health.service import HealthProfileService

router = APIRouter(prefix="/health-profile", tags=["Unified Health Profile & Conditions"])

# --- Allergies ---
@router.post("/allergies", response_model=ApiResponse[AllergyResponse], status_code=status.HTTP_201_CREATED)
async def add_allergy(
    req: AllergyCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[AllergyResponse]:
    """Record an allergy entry with reaction and severity."""
    service = HealthProfileService(db)
    a = await service.create_allergy(current_user.id, req)
    payload = AllergyResponse(
        id=a.id,
        allergen=a.allergen,
        reaction=a.reaction,
        severity=a.severity.value if hasattr(a.severity, "value") else str(a.severity),
        is_active=a.is_active,
    )
    return ApiResponse[AllergyResponse](success=True, message="Allergy recorded", data=payload)

@router.get("/allergies", response_model=ApiResponse[List[AllergyResponse]], status_code=status.HTTP_200_OK)
async def get_allergies(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[AllergyResponse]]:
    """Retrieve recorded allergies."""
    service = HealthProfileService(db)
    allergies = await service.get_allergies(current_user.id)
    payload = [
        AllergyResponse(
            id=a.id,
            allergen=a.allergen,
            reaction=a.reaction,
            severity=a.severity.value if hasattr(a.severity, "value") else str(a.severity),
            is_active=a.is_active,
        )
        for a in allergies
    ]
    return ApiResponse[List[AllergyResponse]](success=True, message="Allergies retrieved", data=payload)

@router.delete("/allergies/{allergy_id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_allergy(
    allergy_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = HealthProfileService(db)
    await service.delete_allergy(current_user.id, allergy_id)
    return ApiResponse[dict](success=True, message="Allergy deleted", data={"id": str(allergy_id)})

# --- Medical Conditions ---
@router.post("/conditions", response_model=ApiResponse[ConditionResponse], status_code=status.HTTP_201_CREATED)
async def add_condition(
    req: ConditionCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ConditionResponse]:
    """Record a diagnosed or user-entered medical condition."""
    service = HealthProfileService(db)
    c = await service.create_condition(current_user.id, req)
    payload = ConditionResponse(
        id=c.id,
        condition_name=c.condition_name,
        diagnosed_date=c.diagnosed_date,
        status=c.status.value if hasattr(c.status, "value") else str(c.status),
        notes=c.notes,
    )
    return ApiResponse[ConditionResponse](success=True, message="Medical condition recorded", data=payload)

@router.get("/conditions", response_model=ApiResponse[List[ConditionResponse]], status_code=status.HTTP_200_OK)
async def get_conditions(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[ConditionResponse]]:
    """Retrieve recorded medical conditions."""
    service = HealthProfileService(db)
    conditions = await service.get_conditions(current_user.id)
    payload = [
        ConditionResponse(
            id=c.id,
            condition_name=c.condition_name,
            diagnosed_date=c.diagnosed_date,
            status=c.status.value if hasattr(c.status, "value") else str(c.status),
            notes=c.notes,
        )
        for c in conditions
    ]
    return ApiResponse[List[ConditionResponse]](success=True, message="Conditions retrieved", data=payload)

@router.delete("/conditions/{condition_id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_condition(
    condition_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = HealthProfileService(db)
    await service.delete_condition(current_user.id, condition_id)
    return ApiResponse[dict](success=True, message="Condition deleted", data={"id": str(condition_id)})

# --- Health Goals ---
@router.post("/goals", response_model=ApiResponse[GoalResponse], status_code=status.HTTP_201_CREATED)
async def add_goal(
    req: GoalCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[GoalResponse]:
    """Create a new personal health goal."""
    service = HealthProfileService(db)
    g = await service.create_goal(current_user.id, req)
    payload = GoalResponse(
        id=g.id,
        title=g.title,
        goal_type=g.goal_type,
        target_value=g.target_value,
        current_value=g.current_value,
        unit=g.unit,
        start_date=g.start_date,
        target_date=g.target_date,
        status=g.status.value if hasattr(g.status, "value") else str(g.status),
        notes=g.notes,
    )
    return ApiResponse[GoalResponse](success=True, message="Health goal created", data=payload)

@router.get("/goals", response_model=ApiResponse[List[GoalResponse]], status_code=status.HTTP_200_OK)
async def get_goals(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[List[GoalResponse]]:
    """Retrieve personal health goals."""
    service = HealthProfileService(db)
    goals = await service.get_goals(current_user.id)
    payload = [
        GoalResponse(
            id=g.id,
            title=g.title,
            goal_type=g.goal_type,
            target_value=g.target_value,
            current_value=g.current_value,
            unit=g.unit,
            start_date=g.start_date,
            target_date=g.target_date,
            status=g.status.value if hasattr(g.status, "value") else str(g.status),
            notes=g.notes,
        )
        for g in goals
    ]
    return ApiResponse[List[GoalResponse]](success=True, message="Goals retrieved", data=payload)

@router.delete("/goals/{goal_id}", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def delete_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[dict]:
    service = HealthProfileService(db)
    await service.delete_goal(current_user.id, goal_id)
    return ApiResponse[dict](success=True, message="Goal deleted", data={"id": str(goal_id)})

# --- Lifestyle Profile ---
@router.get("/lifestyle", response_model=ApiResponse[LifestyleResponse], status_code=status.HTTP_200_OK)
async def get_lifestyle(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LifestyleResponse]:
    """Retrieve lifestyle profile (diet, activity, sleep and water targets)."""
    service = HealthProfileService(db)
    lifestyle = await service.get_or_create_lifestyle(current_user.id)
    payload = LifestyleResponse(
        diet_type=lifestyle.diet_type,
        activity_level=lifestyle.activity_level,
        smoking_status=lifestyle.smoking_status,
        alcohol_status=lifestyle.alcohol_status,
        sleep_target_hours=lifestyle.sleep_target_hours,
        water_target_liters=lifestyle.water_target_liters,
    )
    return ApiResponse[LifestyleResponse](success=True, message="Lifestyle profile retrieved", data=payload)

@router.put("/lifestyle", response_model=ApiResponse[LifestyleResponse], status_code=status.HTTP_200_OK)
async def update_lifestyle(
    req: LifestyleUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[LifestyleResponse]:
    """Update lifestyle profile."""
    service = HealthProfileService(db)
    lifestyle = await service.update_lifestyle(current_user.id, req)
    payload = LifestyleResponse(
        diet_type=lifestyle.diet_type,
        activity_level=lifestyle.activity_level,
        smoking_status=lifestyle.smoking_status,
        alcohol_status=lifestyle.alcohol_status,
        sleep_target_hours=lifestyle.sleep_target_hours,
        water_target_liters=lifestyle.water_target_liters,
    )
    return ApiResponse[LifestyleResponse](success=True, message="Lifestyle profile updated", data=payload)

# --- Consolidated Unified Summary ---
@router.get("/summary", response_model=ApiResponse[UnifiedHealthSummaryResponse], status_code=status.HTTP_200_OK)
async def get_health_summary(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UnifiedHealthSummaryResponse]:
    """Retrieve consolidated unified health profile summary for dashboard widgets."""
    service = HealthProfileService(db)
    summary = await service.get_unified_summary(current_user.id)
    return ApiResponse[UnifiedHealthSummaryResponse](
        success=True,
        message="Unified health summary retrieved successfully",
        data=summary,
    )
