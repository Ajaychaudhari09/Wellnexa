from typing import Any, Optional
from fastapi import HTTPException, status

class WellNexaException(HTTPException):
    """Base application exception."""
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = "An unexpected error occurred in WellNexa AI.",
        headers: Optional[dict[str, str]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class NotFoundException(WellNexaException):
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource} with identifier '{identifier}' was not found.",
        )

class UnauthorizedException(WellNexaException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class ForbiddenException(WellNexaException):
    def __init__(self, detail: str = "You do not have permission to access this resource"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

class ConflictException(WellNexaException):
    def __init__(self, detail: str = "A resource conflict occurred"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )
