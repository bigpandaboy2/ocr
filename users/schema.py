from pydantic import BaseModel, EmailStr

class CreateUserRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str

class CreateUserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr