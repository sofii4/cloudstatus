import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings
from app.core.scheduler import start_scheduler, scheduler
from app.database import engine, Base
from app.api import routes_health, routes_status, routes_admin, routes_auth
import app.models.incident  # noqa: F401 — ensure table is created
import app.models.webhook   # noqa: F401 — ensure table is created

logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Banco de dados conectado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao conectar ao banco: {e}")
        raise
    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="CloudStatus API", lifespan=lifespan)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_auth.router, prefix="/api")
app.include_router(routes_status.router, prefix="/api")
app.include_router(routes_admin.router, prefix="/api/admin")
