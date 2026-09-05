from typing import Union
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Vinayak"])
    email: EmailStr = Field(..., examples=["vinayak@example.com"])
    password: str = Field(..., min_length=8, max_length=128, examples=["StrongPassword123"])


class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["vinayak@example.com"])
    password: str = Field(..., examples=["StrongPassword123"])


class UserResponse(BaseModel):
    id: Union[str, int]
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str


class ProtectedResponse(BaseModel):
    message: str
    user_id: Union[str, int]
