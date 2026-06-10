from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["health"])

@router.get("/health", summary="Health check")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": get_settings().service_name,
    }