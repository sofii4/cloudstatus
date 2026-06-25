import secrets
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8

bearer_scheme = HTTPBearer(auto_error=False)

def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": username, "exp": expire}, settings.secret_key, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou ausente",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise exc
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise exc
        return username
    except JWTError:
        raise exc

def verify_credentials(username: str, password: str) -> bool:
    ok_user = secrets.compare_digest(username, settings.admin_username)
    ok_pass = secrets.compare_digest(password, settings.admin_password)
    return ok_user and ok_pass
