from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.service import Service
from app.models.event import Event
from app.services.cache import get_all_statuses, get_service_status
from sqlalchemy import desc

router = APIRouter()

@router.get("/status")
async def get_all_services_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.is_active == True))
    services = result.scalars().all()

    statuses = await get_all_statuses()
    output = []
    for svc in services:
        cached = statuses.get(str(svc.id))
        output.append({
            "id": svc.id,
            "name": svc.name,
            "url": svc.url,
            "current_status": cached,
        })
    return output

@router.get("/status/{service_id}/history")
async def get_service_history(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Event)
        .where(Event.service_id == service_id)
        .order_by(desc(Event.checked_at))
        .limit(288)  # últimas 24h com polling de 5 min
    )
    events = result.scalars().all()
    return events