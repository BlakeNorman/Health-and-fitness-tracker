from .init import get_db, execute_qry, execute_qry_one
from models.running import Run
from models.errors import Duplicate, Missing

from sqlite3 import IntegrityError
from datetime import date

with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS running(
            activity_id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            distance REAL NOT NULL,
            pace REAL NOT NULL,

            FOREIGN KEY(user_name) REFERENCES user(name),
            FOREIGN KEY(activity_id) REFERENCES activity(id) ON DELETE CASCADE
        )
    """
    )

def row_to_model(row: tuple) -> Run:
    return Run(
        activity_id=row[0],
        distance=row[2],
        pace=row[3]
        )

def model_to_dict(run: Run) -> dict:
    return run.model_dump()

def get_all_runs(user_name: str) -> list[Run]:
    qry = """
        SELECT * FROM running
        WHERE user_name=:user_name
    """
    params = {"user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

def get_one_run(activity_id: int, user_name: str) -> Run:
    qry = """
        SELECT * FROM running 
        WHERE activity_id=:activity_id 
        AND user_name=:user_name
    """
    params = {"activity_id": activity_id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    raise Missing(msg="Run does not exist")

def get_runs_by_date(run_date: date, user_name: str) -> list[Run]:
    qry = """
        SELECT running.* FROM running
        JOIN activity
        ON running.activity_id = activity.id
        JOIN daily_log
        ON activity.daily_log_id = daily_log.id
        WHERE daily_log.date=:run_date
        AND running.user_name=:user_name
    """
    params = {"run_date": str(run_date), "user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

def create_run(run: Run, user_name: str) -> Run:
    if not run:
        raise ValueError("Activity cannot be empty")
    qry = """
        INSERT INTO running( 
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
    params = {"user_name": user_name, **model_to_dict(run)}
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            conn.commit()
    except IntegrityError:
        raise Duplicate(msg="Run already exists")
    return get_one_run(run.activity_id, user_name)

def modify_run(run: Run, user_name: str) -> Run:
    if not run:
        raise ValueError("Activity cannot be empty")
    qry = """
        UPDATE running
        SET 
            distance=:distance, 
            pace=:pace
        WHERE activity_id=:activity_id 
        AND user_name=:user_name
    """
    params = {"user_name": user_name, **model_to_dict(run)}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        conn.commit()
        updated = curs.rowcount == 1
    if updated:
        return get_one_run(run.activity_id, user_name)
    raise Missing(msg="Run does not exist")