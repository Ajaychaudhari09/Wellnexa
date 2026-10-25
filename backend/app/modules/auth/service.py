import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.core.exceptions import UnauthorizedException, ConflictException, NotFoundException, ForbiddenException
from app.models.user import User, Role, RoleEnum
from app.models.profile import Profile
from app.models.token import RefreshToken
from app.models.audit import AuditLog
from app.modules.auth.schemas import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_role(self, role_name: RoleEnum) -> Role:
        """Fetch role by name or initialize if not present."""
        query = select(Role).where(Role.name == role_name)
        result = await self.db.execute(query)
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name=role_name, description=f"Default {role_name.value} role")
            self.db.add(role)
            await self.db.flush()
        return role

    async def create_audit_log(
        self,
        action: str,
        resource: str,
        user_id: Optional[uuid.UUID] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> AuditLog:
        """Create an immutable audit log entry."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
        )
        self.db.add(log)
        await self.db.flush()
        return log

    async def register(self, req: UserRegisterRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> User:
        """Register a new user, assign default role, and create basic profile."""
        # Check existing user
        query = select(User).where(User.email == req.email.lower().strip())
        result = await self.db.execute(query)
        if result.scalar_one_or_none():
            raise ConflictException(f"User with email '{req.email}' already exists")

        # Determine role (default to PATIENT, allow DOCTOR/ADMIN if specified)
        role = await self.get_or_create_role(req.role or RoleEnum.PATIENT)

        # Create user
        hashed_pwd = get_password_hash(req.password)
        new_user = User(
            email=req.email.lower().strip(),
            hashed_password=hashed_pwd,
            is_active=True,
            is_verified=False,
            roles=[role],
        )
        self.db.add(new_user)
        await self.db.flush()

        # Create profile
        profile = Profile(
            user_id=new_user.id,
            first_name=req.first_name.strip(),
            last_name=req.last_name.strip(),
        )
        self.db.add(profile)
        new_user.profile = profile
        await self.db.flush()

        # Audit log
        await self.create_audit_log(
            action="USER_REGISTRATION",
            resource="users",
            user_id=new_user.id,
            resource_id=str(new_user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            details={"email": new_user.email, "role": role.name.value if isinstance(role.name, RoleEnum) else str(role.name)},
        )

        return new_user

    async def login(self, req: UserLoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Tuple[User, TokenResponse]:
        """Authenticate user and issue JWT token pair."""
        query = select(User).where(User.email == req.email.lower().strip())
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user or not verify_password(req.password, user.hashed_password):
            # Failed login audit
            await self.create_audit_log(
                action="LOGIN_FAILED",
                resource="auth",
                ip_address=ip_address,
                user_agent=user_agent,
                details={"attempted_email": req.email},
            )
            raise UnauthorizedException("Invalid email or password")

        if not user.is_active:
            raise ForbiddenException("User account is inactive")

        # Issue tokens
        access_token = create_access_token(subject=user.id, extra_claims={"email": user.email})
        refresh_token = create_refresh_token(subject=user.id)

        # Store hashed refresh token in database
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        db_refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            is_revoked=False,
        )
        self.db.add(db_refresh_token)
        await self.db.flush()

        # Successful login audit
        await self.create_audit_log(
            action="LOGIN_SUCCESS",
            resource="auth",
            user_id=user.id,
            resource_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        role_names = [
            r.name.value if hasattr(r.name, "value") else str(r.name)
            for r in user.roles
        ]
        user_resp = UserResponse(
            id=user.id,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
            roles=role_names,
            first_name=user.profile.first_name if user.profile else None,
            last_name=user.profile.last_name if user.profile else None,
        )

        token_response = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_resp,
        )

        return user, token_response

    async def refresh_tokens(self, raw_refresh_token: str) -> TokenResponse:
        """Rotate and issue a new access token using a valid refresh token."""
        try:
            payload = decode_token(raw_refresh_token)
            if payload.get("type") != "refresh":
                raise UnauthorizedException("Invalid token type for refresh")
            user_id = uuid.UUID(payload.get("sub"))
        except Exception as exc:
            raise UnauthorizedException(f"Invalid refresh token: {str(exc)}")

        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        query = select(RefreshToken).where(
            and_(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
            )
        )
        result = await self.db.execute(query)
        stored_token = result.scalar_one_or_none()

        if not stored_token:
            raise UnauthorizedException("Refresh token is expired or has been revoked")

        stored_expires = stored_token.expires_at if stored_token.expires_at.tzinfo else stored_token.expires_at.replace(tzinfo=timezone.utc)
        if stored_expires < datetime.now(timezone.utc):
            raise UnauthorizedException("Refresh token is expired or has been revoked")

        # Fetch user
        user_query = select(User).where(User.id == user_id)
        user_res = await self.db.execute(user_query)
        user = user_res.scalar_one_or_none()
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")

        # Issue new access token
        new_access_token = create_access_token(subject=user.id, extra_claims={"email": user.email})

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=raw_refresh_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def revoke_refresh_token(self, raw_refresh_token: str, user_id: uuid.UUID) -> None:
        """Revoke a refresh token on logout."""
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        query = select(RefreshToken).where(
            and_(
                RefreshToken.token_hash == token_hash,
                RefreshToken.user_id == user_id,
            )
        )
        result = await self.db.execute(query)
        stored_token = result.scalar_one_or_none()
        if stored_token:
            stored_token.is_revoked = True
            await self.db.flush()
