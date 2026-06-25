import logging
from datetime import datetime, timezone
import httpx
from sqlalchemy import select
from app.models.webhook import Webhook
from app.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

async def fire_webhooks(service, event_type: str):
    """Fire all matching webhooks for a service event (down or recover)."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Webhook).where(
                (Webhook.service_id == service.id) | (Webhook.service_id == None)
            )
        )
        webhooks = result.scalars().all()

    targets = []
    for wh in webhooks:
        if event_type == "down" and wh.on_down:
            targets.append(wh.url)
        elif event_type == "recover" and wh.on_recover:
            targets.append(wh.url)

    if not targets:
        return

    payload = {
        "event": event_type,
        "service": service.name,
        "url": service.url,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in targets:
            try:
                await client.post(url, json=payload)
                logger.info(f"[notifier] Webhook enviado para {url} ({event_type})")
            except Exception as e:
                logger.warning(f"[notifier] Falha ao enviar webhook para {url}: {e}")
