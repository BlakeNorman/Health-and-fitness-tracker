from .init import get_db, execute_qry, execute_qry_one
from models.cycling import Cycle
from models.errors import Duplicate, Missing

from sqlite3 import IntegrityError
from datetime import date

with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS cycling(
            activity_id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            distance REAL NOT NULL,
            pace REAL NOT NULL,

            FOREIGN KEY(user_name) REFERENCES user(name),
            FOREIGN KEY(activity_id) REFERENCES activity(id) ON DELETE CASCADE
        )
    """
    )

def row_to_model(row: tuple) -> Cycle:
    return Cycle(
        activity_id=row[0],
        distance=row[2],
        pace=row[3]
        )

def model_to_dict(cycle: Cycle) -> dict:
    return cycle.model_dump()

def get_all_cycles(user_name: str) -> list[Cycle]:
    qry = """
        SELECT * FROM cycling
        WHERE user_name=:user_name
    """
    params = {"user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]
 
def get_one_cycle(activity_id: int, user_name: str) -> Cycle:
    qry = """
        SELECT * FROM cycling 
        WHERE activity_id=:activity_id 
        AND user_name=:user_name
    """
    params = {"activity_id": activity_id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    raise Missing(msg="Cycle does not exist")

def get_cycles_by_date(cycle_date: date, user_name: str) -> list[Cycle]:
    qry = """
        SELECT cycling.* 
        FROM cycling
        JOIN activity
        ON cycling.activity_id = activity.id
        JOIN daily_log
        ON activity.daily_log_id = daily_log.id
        WHERE daily_log.date=:cycle_date
        AND cycling.user_name=:user_name
    """
    params = {"cycle_date": str(cycle_date), "user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

def create_cycle(cycle: Cycle, user_name: str) -> Cycle:
    if not cycle:
        raise ValueError("Activity cannot be empty")
    qry = """
        INSERT INTO cycling( 
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
    params = {"user_name": user_name, **model_to_dict(cycle)}
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            conn.commit()
    except IntegrityError:
        raise Duplicate(msg="Cycle already exists")
    return get_one_cycle(cycle.activity_id, user_name)

def modify_cycle(cycle: Cycle, user_name: str) -> Cycle:
    if not cycle:
        raise ValueError("Activity cannot be empty")
    qry = """
        UPDATE cycling
        SET 
            distance=:distance, 
            pace=:pace
        WHERE activity_id=:activity_id 
        AND user_name=:user_name
    """
    params = {"user_name": user_name, **model_to_dict(cycle)}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        conn.commit()
        updated = curs.rowcount == 1
    if updated:
        return get_one_cycle(cycle.activity_id, user_name)
    raise Missing(msg="Cycle does not exist")