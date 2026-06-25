from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.service import Service
from app.models.webhook import Webhook
from app.core.security import get_current_user
from app.services.checker import check_service
from app.services.cache import set_service_status

router = APIRouter()


class ServiceCreate(BaseModel):
    name: str
    url: str
    check_interval: int = 60
    expected_status_code: int = 200
    timeout_seconds: int = 10
    tags: Optional[str] = None


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    check_interval: Optional[int] = None
    expected_status_code: Optional[int] = None
    timeout_seconds: Optional[int] = None
    tags: Optional[str] = None


class WebhookCreate(BaseModel):
    url: str
    service_id: Optional[int] = None
    on_down: bool = True
    on_recover: bool = True


# ── Serviços ─────────────────────────────────────────────────────────────────

@router.get("/services")
async def list_services(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    result = await db.execute(select(Service))
    return result.scalars().all()


@router.post("/services", status_code=status.HTTP_201_CREATED)
async def create_service(
    body: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    svc = Service(**body.model_dump())
    db.add(svc)
    await db.commit()
    await db.refresh(svc)
    return svc


@router.patch("/services/{service_id}")
async def update_service(
    service_id: int,
    body: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(svc, field, value)
    await db.commit()
    await db.refresh(svc)
    return svc


@router.post("/services/{service_id}/toggle", status_code=status.HTTP_200_OK)
async def toggle_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    svc.is_active = not svc.is_active
    await db.commit()
    return {"id": svc.id, "is_active": svc.is_active}


@router.post("/services/{service_id}/check", status_code=status.HTTP_200_OK)
async def manual_check(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    data = await check_service(svc)
    await set_service_status(svc.id, data)
    return data


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    await db.delete(svc)
    await db.commit()


# ── Webhooks ──────────────────────────────────────────────────────────────────

@router.get("/webhooks")
async def list_webhooks(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    result = await db.execute(select(Webhook))
    return result.scalars().all()


@router.post("/webhooks", status_code=status.HTTP_201_CREATED)
async def create_webhook(
    body: WebhookCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    wh = Webhook(**body.model_dump())
    db.add(wh)
    await db.commit()
    await db.refresh(wh)
    return wh


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook(
    webhook_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(get_current_user),
):
    result = await db.execute(select(Webhook).where(Webhook.id == webhook_id))
    wh = result.scalar_one_or_none()
    if not wh:
        raise HTTPException(status_code=404, detail="Webhook não encontrado")
    await db.delete(wh)
    await db.commit()
