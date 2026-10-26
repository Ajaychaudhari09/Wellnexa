import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import NotFoundException
from app.core.encryption import encrypt
from app.models.profile import Profile, GenderEnum, BloodGroupEnum
from app.models.user import User
from app.models.audit import AuditLog
from app.modules.profile.schemas import ProfileCreateUpdateRequest

class ProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile_by_user_id(self, user_id: uuid.UUID) -> Profile:
        """Fetch user profile or raise 404."""
        query = select(Profile).where(Profile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundException("Profile", user_id)
        return profile

    async def update_profile(self, user_id: uuid.UUID, req: ProfileCreateUpdateRequest) -> Profile:
        """Create or update user profile."""
        query = select(Profile).where(Profile.user_id == user_id)
        result = await self.db.execute(query)
        profile = result.scalar_one_or_none()

        if not profile:
            profile = Profile(
                user_id=user_id,
                first_name=encrypt(req.first_name),
                last_name=encrypt(req.last_name),
                phone_number=encrypt(req.phone_number) if req.phone_number else None,
                date_of_birth=req.date_of_birth,
                gender=req.gender,
                blood_group=req.blood_group,
                emergency_contact_name=encrypt(req.emergency_contact_name) if req.emergency_contact_name else None,
                emergency_contact_phone=encrypt(req.emergency_contact_phone) if req.emergency_contact_phone else None,
            )
            self.db.add(profile)
        else:
            profile.first_name = encrypt(req.first_name)
            profile.last_name = encrypt(req.last_name)
            profile.phone_number = encrypt(req.phone_number) if req.phone_number else None
            profile.date_of_birth = req.date_of_birth
            profile.gender = req.gender
            profile.blood_group = req.blood_group
            profile.emergency_contact_name = encrypt(req.emergency_contact_name) if req.emergency_contact_name else None
            profile.emergency_contact_phone = encrypt(req.emergency_contact_phone) if req.emergency_contact_phone else None

        await self.db.flush()

        # Audit log for profile update
        audit = AuditLog(
            user_id=user_id,
            action="PROFILE_UPDATED",
            resource="profiles",
            resource_id=str(profile.id),
        )
        self.db.add(audit)
        await self.db.flush()

        return profile
