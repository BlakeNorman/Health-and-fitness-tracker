from models.user import User, PasswordReset
from models.errors import Missing, Duplicate
from .init import get_db, execute_qry, execute_qry_one

from sqlite3 import IntegrityError
from datetime import datetime

# Create a table to store usernames and associated hashed passwords
# Also create a table to store usernames and associated hashed passwords 
# of deleted accounts
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

# Get the information stored in a row of the user table 
# and use that to create a user object
def row_to_model(row: tuple) -> User:
    return User(
        name=row[0], 
        email=row[1],
        password_hash=row[2]
    )

# Take in a user object and convert the user information 
# to a dictionary
def model_to_dict(user: User) -> dict:
    return user.model_dump()

# Get the information stored in a row of the user table, 
# use that information to create a user object, and return the user object
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

# For each row in the user table, create a user object, 
# then return all user objects
def get_all() -> list[User]:
    qry = """
        SELECT * FROM user
    """
    rows = execute_qry(qry)
    return [row_to_model(row) for row in rows]

# Take in a user object and store the information in the 
# user object in the user table
def create(user: User) -> User:
    """Add <user> to user table"""
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

# Take in an existing name and change the row in the user table 
# associated to that name so that is has the name 
# and hashed password associated with the input user object
def modify(name: str, user: User) -> User:
    qry = """
        UPDATE user 
        SET 
            name=:name, 
            email=:email,
            password_hash=:password_hash
        WHERE name=:name0
    """
    params = {
        "name": user.name,
        "email": user.email,
        "password_hash": user.password_hash,
        "name0": name
    }
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
    except IntegrityError:
        raise Duplicate(msg=f"User {user.name} already exists")
    if curs.rowcount == 1:
        return get_one(user.name)
    else:
        raise Missing(msg=f"User {name} not found")

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

def delete(name: str) -> None:
    """Delete user with <name> from user table, add to xuser table"""
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