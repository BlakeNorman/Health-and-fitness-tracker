from .init import get_db, execute_qry, execute_qry_one
from models.walking import Walk
from models.errors import Duplicate, Missing

from sqlite3 import IntegrityError
from datetime import date

with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS walking(
            activity_id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            distance REAL NOT NULL,
            pace REAL NOT NULL,

            FOREIGN KEY(user_name) REFERENCES user(name),
            FOREIGN KEY(activity_id) REFERENCES activity(id) ON DELETE CASCADE
        )
    """
    )

def row_to_model(row: tuple) -> Walk:
    return Walk(
        activity_id=row[0],
        distance=row[2],
        pace=row[3]
        )

def model_to_dict(walk: Walk) -> dict:
    return walk.model_dump()

def get_all_walks(user_name: str) -> list[Walk]:
    qry = """
        SELECT * FROM walking
        WHERE user_name=:user_name
    """
    params = {"user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

def get_one_walk(activity_id: int, user_name: str) -> Walk:
    qry = """
        SELECT * FROM walking 
        WHERE activity_id=:activity_id 
        AND user_name=:user_name
    """
    params = {"activity_id": activity_id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    raise Missing(msg="Walk does not exist")

def get_walks_by_date(walk_date: date, user_name: str) -> list[Walk]:
    qry = """
        SELECT walking.* 
        FROM walking
        JOIN activity
        ON running.activity_id = activity.id
        JOIN daily_log
        ON activity.daily_log_id = daily_log.id
        WHERE daily_log.date=:walk_date
        AND walking.user_name=:user_name
    """
    params = {"walk_date": str(walk_date), "user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

def create_walk(walk: Walk, user_name: str) -> Walk:
    if not walk:
        raise ValueError("Activity cannot be empty")
    qry = """
        INSERT INTO walking(
            activity_id, 
            user_name, 
            distance, 
            pace
        )
        VALUES(
            :activity_id, 
            :user_name, 
            :distance, 
            :pace
        )
    """
    params = {"user_name": user_name, **model_to_dict(walk)}
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            conn.commit()
    except IntegrityError:
        raise Duplicate(msg="Walk already exists")
    return get_one_walk(walk.activity_id, user_name)

def modify_walk(walk: Walk, user_name: str) -> Walk:
    if not walk:
        raise ValueError("Activity cannot be empty")
    qry = """
        UPDATE walking
        SET 
            distance=:distance, 
            pace=:pace
        WHERE activity_id=:activity_id 
        AND user_name=:user_name
    """
    params = {"user_name": user_name, **model_to_dict(walk)}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        conn.commit()
        updated = curs.rowcount == 1
    if updated:
        return get_one_walk(walk.activity_id, user_name)
    raise Missing(msg="Walk does not exist")