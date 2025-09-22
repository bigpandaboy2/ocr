from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from users.models import UserModel
from users.responses import UserResponse
from users.schema import CreateUserRequest
from users.services import create_user_account

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def create_user(data: CreateUserRequest, db: AsyncSession = Depends(get_db)):
    new_user = await create_user_account(data=data, db=db)
    return UserResponse.model_validate(new_user)

@user_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_detail(current_user: UserModel = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
