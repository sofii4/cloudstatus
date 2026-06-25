from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from app.core.security import create_access_token, verify_credentials

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/auth/login")
async def login(body: LoginRequest):
    if not verify_credentials(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )
    token = create_access_token(body.username)
    return {"access_token": token, "token_type": "bearer"}
