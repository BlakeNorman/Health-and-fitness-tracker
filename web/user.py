from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.user import User, UserCreate, PasswordUpdate, PasswordConfirmation, PasswordResetRequest, PasswordResetNewPassword
from datetime import timedelta
import service.user as user_service
import service.email as email_service
from models.errors import Missing, Duplicate

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/user")

oauth2_dep = OAuth2PasswordBearer(tokenUrl="/user/token")

def raise_unauthed():
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"}
    )

def get_current_user(token: str = Depends(oauth2_dep)) -> User:
    user = user_service.get_current_user(token)
    if user is None:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token", 
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

@router.post("/token")
async def create_access_token(
        form_data: OAuth2PasswordRequestForm = Depends()
    ):
    """Authenticate user, then return JWT access token"""
    user = user_service.auth_user(form_data.username, form_data.password)
    if user is None:
        raise_unauthed()
    expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = user_service.create_access_token(
        payload={"sub": user.name}, 
        expires=expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/token")
def get_access_token(token: str = Depends(oauth2_dep)) -> dict:
    """Return the current access token"""
    return {"token": token}

@router.post("/register")
def register_user(user: UserCreate):
    try:
        user_service.register_user(user.name, user.email, user.password)
        return {"message": "Account created"}
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.post("/forgot-password")
def request_password_reset(email: PasswordResetRequest):
    message = {
        "message": "A reset link has been sent to the provided email address"
    }
    try:
        token = user_service.request_password_reset(email.email)
    except Missing:
        return message
    link = f"/reset-password/{token}"
    email_service.send_password_reset_email(email.email, link)
    return message

@router.post("/reset-password/{token}")
def reset_password(token, password: PasswordResetNewPassword) -> User:
    return user_service.reset_password(token, password.password)

@router.patch("/account") 
def modify_password(passwords: PasswordUpdate, user: User = Depends(get_current_user)) -> User:
    if user_service.auth_user(user.name, passwords.current_password):
        return user_service.modify_password(passwords.new_password, user)
    raise HTTPException(status_code=401, detail="Incorrect current password")

@router.delete("/account")
def delete_account(
        password: PasswordConfirmation, 
        user: User = Depends(get_current_user)
    ) -> None:
    if not user_service.verify_password(password.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect password")
    user_service.delete(user.name)