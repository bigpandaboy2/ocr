from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from users.models import UserModel
from users.schema import CreateUserRequest
from core.security import get_password_hash

async def create_user_account(data: CreateUserRequest, db: AsyncSession):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    result = await db.execute(select(UserModel).where(UserModel.email == data.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = UserModel(
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        password=get_password_hash(data.password),
        is_active=True,
        is_verified=False,
        registered_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
