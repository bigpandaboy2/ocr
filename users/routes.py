from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db
from users.schema import CreateUserRequest
from users.services import create_user_account

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(data: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    await create_user_account(data=data, db=db)
    return JSONResponse(
        content={"message": "User created successfully"},
        status_code=status.HTTP_201_CREATED,
    )