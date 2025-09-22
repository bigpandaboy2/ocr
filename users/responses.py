from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class ORMResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserResponse(ORMResponse):

    id: int
    first_name: str
    last_name: str
    email: EmailStr
    registered_at: Optional[datetime] = None
