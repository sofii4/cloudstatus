from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.service import Service
from app.core.config import settings
import secrets

router = APIRouter()
security = HTTPBasic()

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    ok_user = secrets.compare_digest(credentials.username, settings.admin_username)
    ok_pass = secrets.compare_digest(credentials.password, settings.admin_password)
    if not (ok_user and ok_pass):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@router.get("/services")
async def list_services(
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_admin)
):
    result = await db.execute(select(Service))
    return result.scalars().all()

@router.post("/services", status_code=status.HTTP_201_CREATED)
async def create_service(
    name: str,
    url: str,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_admin)
):
    svc = Service(name=name, url=url)
    db.add(svc)
    await db.commit()
    await db.refresh(svc)
    return svc

@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_service(
    service_id: int,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(verify_admin)
):
    result = await db.execute(select(Service).where(Service.id == service_id))
    svc = result.scalar_one_or_none()
    if not svc:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    await db.delete(svc)
    await db.commit()