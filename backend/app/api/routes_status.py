from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime, timedelta, timezone
from app.database import get_db
from app.models.service import Service
from app.models.event import Event
from app.models.incident import Incident
from app.services.cache import get_all_statuses

router = APIRouter()


def _uptime_pct(events: list) -> float:
    if not events:
        return None
    up = sum(1 for e in events if e.is_up)
    return round(up / len(events) * 100, 1)


@router.get("/status")
async def get_all_services_status(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Service).where(Service.is_active == True))
    services = result.scalars().all()

    statuses = await get_all_statuses()
    cutoff_24h = datetime.now(timezone.utc) - timedelta(hours=24)

    output = []
    for svc in services:
        cached = statuses.get(str(svc.id))

        # últimas 30 checagens para a barra visual
        events_result = await db.execute(
            select(Event)
            .where(Event.service_id == svc.id)
            .order_by(desc(Event.checked_at))
            .limit(30)
        )
        recent_events = list(reversed(events_result.scalars().all()))

        # uptime 24h
        events_24h_result = await db.execute(
            select(Event).where(
                Event.service_id == svc.id,
                Event.checked_at >= cutoff_24h,
            )
        )
        events_24h = events_24h_result.scalars().all()

        # incidente aberto
        open_inc = await db.execute(
            select(Incident).where(
                Incident.service_id == svc.id,
                Incident.resolved_at == None,
            )
        )
        open_incident = open_inc.scalar_one_or_none()

        output.append({
            "id": svc.id,
            "name": svc.name,
            "url": svc.url,
            "tags": svc.tags,
            "check_interval": svc.check_interval,
            "current_status": cached,
            "uptime_24h": _uptime_pct(events_24h),
            "history": [{"is_up": e.is_up, "checked_at": e.checked_at.isoformat()} for e in recent_events],
            "open_incident": {
                "id": open_incident.id,
                "started_at": open_incident.started_at.isoformat(),
            } if open_incident else None,
        })
    return output


@router.get("/status/{service_id}/history")
async def get_service_history(service_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Event)
        .where(Event.service_id == service_id)
        .order_by(desc(Event.checked_at))
        .limit(288)
    )
    return result.scalars().all()


@router.get("/stats/{service_id}")
async def get_service_stats(service_id: int, db: AsyncSession = Depends(get_db)):
    now = datetime.now(timezone.utc)

    async def uptime_for_period(hours: int):
        cutoff = now - timedelta(hours=hours)
        res = await db.execute(
            select(Event).where(
                Event.service_id == service_id,
                Event.checked_at >= cutoff,
            )
        )
        events = res.scalars().all()
        return _uptime_pct(events)

    # avg response time (last 24h, excluding None)
    res = await db.execute(
        select(Event).where(
            Event.service_id == service_id,
            Event.checked_at >= now - timedelta(hours=24),
            Event.response_ms != None,
        )
    )
    events_24h = res.scalars().all()
    avg_ms = round(sum(e.response_ms for e in events_24h) / len(events_24h), 1) if events_24h else None

    # incident count (last 30d)
    res_inc = await db.execute(
        select(func.count(Incident.id)).where(
            Incident.service_id == service_id,
            Incident.started_at >= now - timedelta(days=30),
        )
    )
    incident_count = res_inc.scalar()

    return {
        "service_id": service_id,
        "uptime_24h": await uptime_for_period(24),
        "uptime_7d": await uptime_for_period(168),
        "uptime_30d": await uptime_for_period(720),
        "avg_response_ms_24h": avg_ms,
        "incidents_30d": incident_count,
    }


@router.get("/incidents")
async def list_incidents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Incident, Service.name.label("service_name"))
        .join(Service, Incident.service_id == Service.id)
        .order_by(desc(Incident.started_at))
        .limit(20)
    )
    rows = result.all()
    return [
        {
            "id": row.Incident.id,
            "service_id": row.Incident.service_id,
            "service_name": row.service_name,
            "started_at": row.Incident.started_at.isoformat(),
            "resolved_at": row.Incident.resolved_at.isoformat() if row.Incident.resolved_at else None,
            "duration_seconds": row.Incident.duration_seconds,
        }
        for row in rows
    ]
