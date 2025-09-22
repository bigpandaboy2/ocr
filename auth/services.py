from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.responses import TokenResponse
from core.config import get_settings
from core.security import create_access_token, create_refresh_token, get_token_payload, verify_password
from users.models import UserModel

settings = get_settings()

async def get_token(data, db: AsyncSession):
    result = await db.execute(select(UserModel).where(UserModel.email == data.username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Email is not registered with us.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=400,
            detail="Invalid login credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    _verify_user_access(user=user)

    return await _get_user_token(user=user)

async def get_refresh_token(token: str, db: AsyncSession):
    payload = get_token_payload(token=token)
    if not payload or not isinstance(payload, dict):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("id")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Your account is inactive. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return await _get_user_token(user=user, refresh_token=token)

def _verify_user_access(user: UserModel):
    if not user.is_active:
        raise HTTPException(
            status_code=400,
            detail="Your account is inactive. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
       raise HTTPException(
            status_code=400,
            detail="Your account is unverified. We have resend the account verification email.",
            headers={"WWW-Authenticate": "Bearer"},
        ) 

async def _get_user_token(user: UserModel, refresh_token: str | None = None):
    payload = {"id": user.id}

    access_token_expire = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = await create_access_token(payload, access_token_expire)
    if not refresh_token:
        refresh_token = await create_refresh_token(payload)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(access_token_expire.total_seconds()),
    )
