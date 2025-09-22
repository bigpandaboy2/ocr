from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    UnauthenticatedUser,
)
from fastapi import Depends, HTTPException

from core.database import AsyncSessionLocal, get_db
from users.models import UserModel

from core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

settings = get_settings()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def create_access_token(data, expiry: timedelta):
    payload = data.copy()
    expire_in = datetime.now(timezone.utc) + expiry
    payload.update({"exp": expire_in})
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def create_refresh_token(data):
    return jwt.encode(data, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def get_token_payload(token):
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None
    return payload

async def _resolve_user(token: str, db: AsyncSession) -> UserModel | None:
    payload = get_token_payload(token)
    if not isinstance(payload, dict):
        return None

    user_id = payload.get("id")
    if not user_id:
        return None

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    user = await _resolve_user(token, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


class JWTAuth(AuthenticationBackend):

    async def authenticate(self, conn):
        guest = AuthCredentials(['unauthenticated']), UnauthenticatedUser()

        auth_header = conn.headers.get('authorization')
        if not auth_header or not auth_header.lower().startswith('bearer '):
            return guest

        token = auth_header.split(' ', 1)[1].strip()
        if not token:
            return guest

        try:
            async with AsyncSessionLocal() as session:
                user = await _resolve_user(token, session)
        except Exception:
            return guest

        if not user:
            return guest

        return AuthCredentials(['authenticated']), user
