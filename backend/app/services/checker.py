import httpx
import logging
import time
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.service import Service
from app.models.event import Event
from app.models.incident import Incident
from app.services.cache import set_service_status, get_service_status
from app.services.notifier import fire_webhooks
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def check_service(service: Service) -> dict:
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=float(service.timeout_seconds), follow_redirects=True) as client:
            response = await client.get(service.url)
        elapsed_ms = (time.monotonic() - start) * 1000
        is_up = response.status_code == service.expected_status_code
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


async def _handle_state_change(db: AsyncSession, service: Service, prev_up, is_up: bool):
    """Open or close an incident when service state transitions."""
    if prev_up is True and not is_up:
        # Service went down — open incident
        incident = Incident(service_id=service.id)
        db.add(incident)
        await db.flush()
        logger.info(f"[incident] Incidente aberto para {service.name} (id={incident.id})")
        await fire_webhooks(service, "down")

    elif prev_up is False and is_up:
        # Service recovered — close open incident
        result = await db.execute(
            select(Incident).where(
                Incident.service_id == service.id,
                Incident.resolved_at == None,
            )
        )
        incident = result.scalar_one_or_none()
        if incident:
            now = datetime.now(timezone.utc)
            incident.resolved_at = now
            started = incident.started_at.replace(tzinfo=timezone.utc) if incident.started_at.tzinfo is None else incident.started_at
            incident.duration_seconds = (now - started).total_seconds()
            logger.info(f"[incident] Incidente resolvido para {service.name} ({incident.duration_seconds:.0f}s)")
        await fire_webhooks(service, "recover")


async def run_all_checks():
    logger.info("[scheduler] Iniciando ciclo de polling...")
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Service).where(Service.is_active == True)
        )
        services = result.scalars().all()

        for service in services:
            prev_cached = await get_service_status(service.id)
            prev_up = prev_cached.get("is_up") if prev_cached else None

            data = await check_service(service)

            event = Event(service_id=service.id, **data)
            db.add(event)

            await _handle_state_change(db, service, prev_up, data["is_up"])
            await set_service_status(service.id, data)

            logger.info(
                f"[checker] {service.name} | up={data['is_up']} "
                f"| {data['response_ms']}ms | status={data['status_code']}"
            )

        await db.commit()
    logger.info("[scheduler] Ciclo concluído.")
