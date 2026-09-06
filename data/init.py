from pathlib import Path
from sqlite3 import connect, Connection

def get_db() -> Connection:
    """Create and return a connection to the SQLite database"""

    # get the absolute normalized path to fitness.db
    db_path = Path(__file__).resolve().parents[1] / "db" / "Health-and-fitness.db"

    # open a connection to the database
    conn = connect(db_path)

    # make the database enforce foreign keys (and on delete cascade)
    conn.execute("PRAGMA foreign_keys = ON")

    # return the connection to the database when this function is called
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

    