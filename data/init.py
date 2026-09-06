from pathlib import Path
from sqlite3 import connect, Connection

def get_db() -> Connection:
    db_path = Path(__file__).resolve().parents[1] / "db" / "Health-and-fitness.db"
    conn = connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn 

def execute_qry(qry, params=None):
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params or {})
        return curs.fetchall()
    
def execute_qry_one(qry, params=None):
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params or {})
        return curs.fetchone()

    