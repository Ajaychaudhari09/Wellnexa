from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    """Standardized top-level API response envelope."""
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[T] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated list envelope."""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class HealthStatus(BaseModel):
    """System health check response payload."""
    status: str = Field(..., description="Overall system status (healthy/degraded)")
    environment: str = Field(..., description="Active environment name")
    version: str = Field(..., description="Backend release version")
    timestamp: datetime = Field(..., description="Current server time (UTC)")
    database: str = Field(..., description="Database connectivity status")
