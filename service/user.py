from models.user import User, PasswordReset
from models.errors import Missing
import data.user as user_data

from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
import secrets
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = "HS256"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash plain and compare with hash from database
def verify_password(plain: str, hash: str) -> bool:
    return password_context.verify(plain, hash)

# Hash a plain string
def get_hash(plain: str) -> str:
    return password_context.hash(plain)

def get_jwt_username(token: str) -> str | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not (username := payload.get("sub")):
            return None
    except JWTError:
        return None
    return username

def lookup_user(username: str) -> User | None:
    try:
        return user_data.get_one(username)
    except Missing:
        return None

def get_current_user(token: str) -> User | None:
    username = get_jwt_username(token)
    if username is None:
        return None
    return lookup_user(username)

# Authenticate user
def auth_user(name: str, plain: str) -> User | None:
    user = lookup_user(name)
    if user is None:
        return None
    if not verify_password(plain, user.password_hash):
        return None
    return user

def create_access_token(payload: dict, expires: timedelta | None = None):
    claims = payload.copy()
    now = datetime.now(timezone.utc)
    if not expires:
        expires = timedelta(minutes=15)
    claims.update({"exp": now + expires})
    encoded_jwt = jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def register_user(name: str, email: str, plain: str) -> User:
    hashed = get_hash(plain)
    user = User(name=name, email=email, password_hash=hashed)
    return user_data.create(user)

def modify_password(new_password: str, user: User) -> User:
    new_password_hash = get_hash(new_password)
    return user_data.modify_password(new_password_hash, user)

###########################################################
# Password Reset
###########################################################

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def request_password_reset(email: str) -> str:
    user = user_data.get_user_by_email(email)
    user_data.invalidate_password_resets(user.name)
    token = generate_reset_token()
    token_hash = hash_reset_token(token)
    expires = datetime.now(timezone.utc)+timedelta(minutes=30)
    user_data.create_password_reset(
        user_name=user.name, 
        token_hash=token_hash, 
        expires=expires
    )
    return token

def validate_reset_token(token: str) -> PasswordReset:
    token_hash = hash_reset_token(token)
    reset = user_data.get_password_reset_by_token(token_hash)
    if reset.used:
        raise ValueError("Password reset token has already expired or been used")
    if reset.expires <= datetime.now(timezone.utc):
        raise ValueError("Password reset token has expired")
    return reset

def reset_password(token: str, new_password: str) -> User:
    reset = validate_reset_token(token)
    user = user_data.get_one(reset.user_name)
    new_password_hash = get_hash(new_password)
    user = user_data.modify_password(new_password_hash, user)
    user_data.use_password_reset(reset.id)
    return user

###########################################################
# Passthrough stuff
###########################################################

def get_all() ->list[User]:
    return user_data.get_all()

def get_one(name: str) -> User:
    return user_data.get_one(name)

def create(user: User) -> User:
    return user_data.create(user)

def delete(name: str) -> None:
    return user_data.delete(name)