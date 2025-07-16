from typing import List
from fastapi import APIRouter, Depends

from models.responses import HealthResponse

router = APIRouter(tags=["health"])


def get_registered_keys():
    """Dependency to get registered keys from app state."""
    from main import app
    return getattr(app.state, 'registered_keys', [])


@router.get("/", response_model=HealthResponse)
async def root(registered_keys: List[bytes] = Depends(get_registered_keys)):
    """Health check endpoint."""
    return HealthResponse(
        service="Sensor Key Registry",
        status="active",
        registered_keys_count=len(registered_keys)
    )
