from models.user import User, PasswordReset
from models.errors import Missing, Duplicate
from .init import get_db, execute_qry, execute_qry_one

from sqlite3 import IntegrityError
from datetime import datetime

# user table
with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS user(
            name TEXT PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT
        )
    """
    )
# xuser table
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS xuser(
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            password_hash TEXT
        )
    """
    )
# password_reset table
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS password_reset(
            id INTEGER PRIMARY KEY,
            user_name TEXT,
            token_hash TEXT,
            expires TEXT,
            used INTEGER DEFAULT 0
        )
    """
    )

def row_to_model(row: tuple) -> User:
    return User(
        name=row[0], 
        email=row[1],
        password_hash=row[2]
    )

def model_to_dict(user: User) -> dict:
    return user.model_dump()

def get_one(name: str) -> User:
    qry = """
        SELECT * FROM user WHERE name=:name
    """
    params = {"name": name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    else:
        raise Missing(msg=f"User {name} not found")

def get_all() -> list[User]:
    qry = """
        SELECT * FROM user
    """
    rows = execute_qry(qry)
    return [row_to_model(row) for row in rows]

def create(user: User) -> User:
    qry = """
        INSERT INTO user(
            name, 
            email,
            password_hash
        ) 
        VALUES( 
            :name, 
            :email,
            :password_hash
        )
    """
    params = model_to_dict(user)
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
    except IntegrityError:
        raise Duplicate(msg=f"User {user.name} already exists")
    return get_one(user.name)

def modify_password(new_password_hash: str, user: User) -> User:
    qry = """
        UPDATE user
        SET
            password_hash=:new_password_hash
        WHERE name=:name 
    """
    params = {
        "name": user.name,
        "new_password_hash": new_password_hash
    }
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
    if curs.rowcount == 1:
        return get_one(user.name)
    else:
        raise Missing(msg=f"User {user.name} not found")

# Delete user from user table and add to xuser table
def delete(name: str) -> None:
    user = get_one(name)
    qry = """
        DELETE FROM user 
        WHERE name=:name
    """
    params = {"name": name}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        if curs.rowcount != 1:
            raise Missing(msg=f"User {name} not found")
        qry = """
            INSERT INTO xuser(
                name, 
                email,
                password_hash
            )
            VALUES(
                :name, 
                :email,
                :password_hash
            )
        """
        params = model_to_dict(user)
        curs.execute(qry, params)


##########################################################
# Password Reset
##########################################################

def reset_row_to_model(row: tuple) -> PasswordReset:
    return PasswordReset(
        id=row[0],
        user_name=row[1],
        token_hash=row[2],
        expires=datetime.fromisoformat(row[3]),
        used=row[4]
    )

def get_user_by_email(email: str) -> User:
    qry = """
        SELECT * FROM user WHERE email=:email    
    """
    params = {"email": email}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    else:
        raise Missing(msg=f"User not found")

def get_password_reset(reset_id: int) -> PasswordReset:
    qry = """
        SELECT * FROM password_reset
        WHERE id=:reset_id
    """
    params = {
        "reset_id": reset_id
    }
    row = execute_qry_one(qry, params)
    if row:
        return reset_row_to_model(row)
    raise Missing(msg=f"Password reset {reset_id} not found")

def get_password_reset_by_token(token_hash: str) -> PasswordReset:
    qry = """
        SELECT * FROM password_reset
        WHERE token_hash=:token_hash
    """
    params = {
        "token_hash": token_hash
    }
    row = execute_qry_one(qry, params)
    if row:
        return reset_row_to_model(row)
    raise Missing(msg=f"Password reset not found")

def create_password_reset(
        user_name: str,
        token_hash: str,
        expires: datetime
    ) -> PasswordReset:
    qry = """
        INSERT INTO password_reset(
            user_name,
            token_hash,
            expires
        ) 
        VALUES(
            :user_name,
            :token_hash,
            :expires
        )   
    """
    params = {
        "user_name": user_name,
        "token_hash": token_hash,
        "expires": expires.isoformat()
    }
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        reset_id = curs.lastrowid
    return get_password_reset(reset_id)

def use_password_reset(reset_id: int) -> None:
    qry = """
        UPDATE password_reset
        SET used=1
        WHERE id=:reset_id
    """
    params = {
        "reset_id": reset_id
    }
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
    if curs.rowcount != 1:
        raise Missing(msg=f"Password reset {reset_id} not found")

def invalidate_password_resets(user_name: str) -> None:
    qry = """
        UPDATE password_reset
        SET used=1
        WHERE user_name=:user_name
        AND used=0
    """
    params = {
        "user_name": user_name
    }
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)