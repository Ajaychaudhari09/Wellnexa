import uuid
from typing import AsyncGenerator, Callable, List, Optional, Union
import jwt
from fastapi import Depends, Header, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.user import User, RoleEnum

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate JWT Bearer token, resolving the authenticated User."""
    if not credentials or not credentials.credentials:
        raise UnauthorizedException("Authentication token is missing")

    token = credentials.credentials
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise UnauthorizedException("Invalid token type")
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str:
            raise UnauthorizedException("Token payload missing subject identifier")
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError) as exc:
        raise UnauthorizedException(f"Invalid or expired token: {str(exc)}")

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedException("User associated with this token does not exist")
    if not user.is_active:
        raise ForbiddenException("User account is inactive")

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure current user is active."""
    if not current_user.is_active:
        raise ForbiddenException("User account is inactive")
    return current_user

def require_roles(*allowed_roles: Union[RoleEnum, str]) -> Callable:
    """Role-Based Access Control dependency factory."""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        user_role_names = {
            (r.name.value if isinstance(r.name, RoleEnum) else str(r.name))
            for r in current_user.roles
        }
        required_names = {
            (r.value if isinstance(r, RoleEnum) else str(r))
            for r in allowed_roles
        }
        
        # Admin always has bypass access
        if RoleEnum.ADMIN.value in user_role_names:
            return current_user

        if not user_role_names.intersection(required_names):
            raise ForbiddenException(
                f"Access denied. Requires one of roles: {', '.join(required_names)}"
            )
        return current_user

    return role_checker
