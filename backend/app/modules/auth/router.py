from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_active_user, require_roles
from app.schemas.common import ApiResponse
from app.models.user import User, RoleEnum
from app.modules.auth.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    MessageResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    req: UserRegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[UserResponse]:
    """Register a new user with default PATIENT role (or specified role) and generate profile."""
    auth_service = AuthService(db)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    user = await auth_service.register(req, ip_address=ip_address, user_agent=user_agent)
    
    role_names = [
        r.name.value if isinstance(r.name, RoleEnum) else str(r.name)
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

    return ApiResponse[UserResponse](
        success=True,
        message="User registration successful",
        data=user_resp,
    )

@router.post("/login", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_200_OK)
async def login(
    req: UserLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """Authenticate user with email and password and issue JWT token pair."""
    auth_service = AuthService(db)
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    _, token_resp = await auth_service.login(req, ip_address=ip_address, user_agent=user_agent)

    return ApiResponse[TokenResponse](
        success=True,
        message="Login successful",
        data=token_resp,
    )

@router.post("/refresh", response_model=ApiResponse[TokenResponse], status_code=status.HTTP_200_OK)
async def refresh_tokens(
    req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[TokenResponse]:
    """Exchange a valid refresh token for a new access token."""
    auth_service = AuthService(db)
    token_resp = await auth_service.refresh_tokens(req.refresh_token)

    return ApiResponse[TokenResponse](
        success=True,
        message="Tokens refreshed successfully",
        data=token_resp,
    )

@router.post("/logout", response_model=ApiResponse[MessageResponse], status_code=status.HTTP_200_OK)
async def logout(
    req: RefreshTokenRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> ApiResponse[MessageResponse]:
    """Revoke user refresh token and terminate session."""
    auth_service = AuthService(db)
    await auth_service.revoke_refresh_token(req.refresh_token, current_user.id)

    return ApiResponse[MessageResponse](
        success=True,
        message="Logged out successfully",
        data=MessageResponse(message="Session ended and refresh token revoked."),
    )

@router.get("/me", response_model=ApiResponse[UserResponse], status_code=status.HTTP_200_OK)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> ApiResponse[UserResponse]:
    """Retrieve details and roles of current authenticated user."""
    role_names = [
        r.name.value if isinstance(r.name, RoleEnum) else str(r.name)
        for r in current_user.roles
    ]

    user_resp = UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        roles=role_names,
        first_name=current_user.profile.first_name if current_user.profile else None,
        last_name=current_user.profile.last_name if current_user.profile else None,
    )

    return ApiResponse[UserResponse](
        success=True,
        message="User profile retrieved",
        data=user_resp,
    )

@router.get("/doctor-only", response_model=ApiResponse[dict], status_code=status.HTTP_200_OK)
async def doctor_only_test(
    current_user: User = Depends(require_roles(RoleEnum.DOCTOR)),
) -> ApiResponse[dict]:
    """Protected test endpoint for DOCTOR role."""
    return ApiResponse[dict](
        success=True,
        message="Welcome, Doctor!",
        data={"user_id": str(current_user.id), "email": current_user.email},
    )
