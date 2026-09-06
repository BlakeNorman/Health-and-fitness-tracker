from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    name: str
    email: str
    password_hash: str

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class PasswordConfirmation(BaseModel):
    password: str

class PasswordReset(BaseModel):
    id: int | None = None
    user_name: str
    token_hash: str
    expires: datetime
    used: bool = False

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetNewPassword(BaseModel):
    password: str