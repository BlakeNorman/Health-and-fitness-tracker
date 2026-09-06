from .init import get_db, execute_qry, execute_qry_one
from models.daily_log import DailyLogIn, DailyLog
from models.errors import Duplicate, Missing

from sqlite3 import IntegrityError
from datetime import date

with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS daily_log(
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            date TEXT NOT NULL,

            FOREIGN KEY(user_name) REFERENCES user(name),
            UNIQUE(user_name, date)
        )
    """
    )

def row_to_model(row: tuple) -> DailyLog:
    return DailyLog(
        id=row[0],
        date=row[2]
    )

def model_to_dict(log: DailyLog) -> dict:
    return log.model_dump()

def get_all_logs(user_name: str) -> list[DailyLog]:
    qry = """
        SELECT * FROM daily_log
        WHERE user_name=:user_name
    """
    params = {"user_name": user_name}
    rows = execute_qry(qry, params) 
    return [row_to_model(row) for row in rows]

def get_one_log(id: int, user_name: str) -> DailyLog:
    qry = """
        SELECT * FROM daily_log 
        WHERE id=:id 
        AND user_name=:user_name
    """
    params = {"id": id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    raise Missing(msg=f"Log {id} does not exist")

def get_log_by_date(log_date: date, user_name: str) -> DailyLog:
    qry = """
        SELECT * FROM daily_log 
        WHERE date=:log_date 
        AND user_name=:user_name
    """
    params = {"log_date": str(log_date), "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    raise Missing(msg=f"Log on {log_date} does not exist")

def create_log(log: DailyLogIn, user_name: str) -> DailyLog:
    if not log:
        raise ValueError("Log cannot be empty")
    qry = """
        INSERT INTO daily_log(
            user_name, 
            date
        )
        VALUES(
            :user_name, 
            :date
        )
    """
    params = {"date": str(log.date), "user_name": user_name}
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            conn.commit()
            id = curs.lastrowid
    except IntegrityError:
        raise Duplicate(msg=f"Log {log.date} already exists")
    return get_one_log(id, user_name)

def modify_log(log: DailyLog, user_name: str) -> DailyLog:
    if not log:
        raise ValueError("Log cannot be empty")
    qry = """
        UPDATE daily_log
        SET date=:date
        WHERE id=:id 
        AND user_name=:user_name
    """
    params = {"user_name": user_name, **model_to_dict(log)}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        conn.commit()
        if curs.rowcount == 1:
            return get_one_log(log.id, user_name)
    raise Missing(msg=f"Log {log.id} does not exist")

def delete_log(id: int, user_name: str) -> None:
    qry = """
        DELETE FROM daily_log 
        WHERE id=:id 
        AND user_name=:user_name
    """
    params = {"id":id, "user_name": user_name}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        conn.commit()
        if curs.rowcount != 1:
            raise Missing(msg=f"Log {id} does not exist")

# Delete daily log row if no corresponding health or activity logs exist
def delete_if_empty(daily_log_id: int, user_name: str) -> None:
    qry = """
        SELECT 
        EXISTS(
            SELECT 1 FROM health 
            WHERE daily_log_id=:daily_log_id 
            AND user_name=:user_name
        ) 
        AS has_health,
        EXISTS(
            SELECT 1 FROM activity 
            WHERE daily_log_id=:daily_log_id 
            AND user_name=:user_name
        ) 
        AS has_activity
    """
    params = {"daily_log_id": daily_log_id, "user_name": user_name}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        row = curs.fetchone()
        has_health = row[0]
        has_activity = row[1]
        if not has_health and not has_activity:
            qry = """
                DELETE FROM daily_log 
                WHERE id=:daily_log_id AND user_name=:user_name
            """
            curs.execute(qry, params)
            conn.commit()