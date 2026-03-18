import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler, scheduler
from app.database import engine, Base
from app.api import routes_health, routes_status, routes_admin

# Log estruturado
logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Banco de dados conectado com sucesso.")
    except Exception as e:
        logger.error(f"Falha ao conectar ao banco: {e}")
        raise  # força o container a reiniciar em vez de travar
    start_scheduler()
    yield
    scheduler.shutdown()

app = FastAPI(title="CloudStatus API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_health.router)
app.include_router(routes_status.router, prefix="/api")
app.include_router(routes_admin.router, prefix="/api/admin")