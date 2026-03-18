import httpx
import logging
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.service import Service
from app.models.event import Event
from app.services.cache import set_service_status
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def check_service(service: Service) -> dict:
    """Faz a requisição HTTP e retorna o resultado."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(service.url)
        elapsed_ms = (time.monotonic() - start) * 1000
        is_up = response.status_code < 500
        return {
            "is_up": is_up,
            "response_ms": round(elapsed_ms, 2),
            "status_code": response.status_code,
            "error_detail": None,
        }
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        logger.warning(f"[checker] Falha ao checar {service.url}: {e}")
        return {
            "is_up": False,
            "response_ms": round(elapsed_ms, 2),
            "status_code": None,
            "error_detail": str(e)[:500],
        }

async def run_all_checks():
    """Chamada pelo APScheduler: percorre todos os serviços ativos."""
    logger.info("[scheduler] Iniciando ciclo de polling...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Service).where(Service.is_active == True)
        )
        services = result.scalars().all()

        for service in services:
            data = await check_service(service)
            
            # Persiste o evento no banco
            event = Event(service_id=service.id, **data)
            db.add(event)
            
            # Atualiza cache Redis com status atual
            await set_service_status(service.id, data)
            
            logger.info(
                f"[checker] {service.name} | up={data['is_up']} "
                f"| {data['response_ms']}ms | status={data['status_code']}"
            )

        await db.commit()
    logger.info("[scheduler] Ciclo concluído.")