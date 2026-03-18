from fastapi import APIRouter
from app.database import engine
from app.services.cache import redis_client

router = APIRouter()

@router.get("/health")
async def health_check():
    checks = {"api": "ok", "db": "unknown", "redis": "unknown"}
    try:
        async with engine.connect():
            checks["db"] = "ok"
    except Exception:
        checks["db"] = "error"
    try:
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"

    status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": status, "checks": checks}