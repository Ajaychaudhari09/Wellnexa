from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.schemas.common import ApiResponse
from app.models.user import User
from app.modules.profile.schemas import ProfileCreateUpdateRequest, ProfileResponse
from app.modules.profile.service import ProfileService

router = APIRouter(prefix="/profile", tags=["Health Profile"])

@router.get("/me", response_model=ApiResponse[ProfileResponse], status_code=status.HTTP_200_OK)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ProfileResponse]:
    """Retrieve the personal profile of the authenticated user."""
    service = ProfileService(db)
    profile = await service.get_profile_by_user_id(current_user.id)

    payload = ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        phone_number=profile.phone_number,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender.value if hasattr(profile.gender, "value") else str(profile.gender),
        blood_group=profile.blood_group.value if hasattr(profile.blood_group, "value") else str(profile.blood_group),
        emergency_contact_name=profile.emergency_contact_name,
        emergency_contact_phone=profile.emergency_contact_phone,
    )

    return ApiResponse[ProfileResponse](
        success=True,
        message="Profile retrieved successfully",
        data=payload,
    )

@router.put("/me", response_model=ApiResponse[ProfileResponse], status_code=status.HTTP_200_OK)
async def update_my_profile(
    req: ProfileCreateUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[ProfileResponse]:
    """Create or update personal profile details."""
    service = ProfileService(db)
    profile = await service.update_profile(current_user.id, req)

    payload = ProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        first_name=profile.first_name,
        last_name=profile.last_name,
        phone_number=profile.phone_number,
        date_of_birth=profile.date_of_birth,
        gender=profile.gender.value if hasattr(profile.gender, "value") else str(profile.gender),
        blood_group=profile.blood_group.value if hasattr(profile.blood_group, "value") else str(profile.blood_group),
        emergency_contact_name=profile.emergency_contact_name,
        emergency_contact_phone=profile.emergency_contact_phone,
    )

    return ApiResponse[ProfileResponse](
        success=True,
        message="Profile updated successfully",
        data=payload,
    )
