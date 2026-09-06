from .init import get_db, execute_qry, execute_qry_one
from models.weightlifting import Weightlifting, WeightliftingExercise, WeightliftingUpdate
from models.errors import Duplicate, Missing

from sqlite3 import IntegrityError
from datetime import date

# weightlifting table
with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS weightlifting(
            activity_id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,

            FOREIGN KEY(user_name) REFERENCES user(name),
            FOREIGN KEY(activity_id) REFERENCES activity(id) ON DELETE CASCADE
        )
    """
    )
# exercises table
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS weightlifting_exercises(
            id INTEGER PRIMARY KEY,
            activity_id INTEGER NOT NULL,
            exercise TEXT NOT NULL,
            weight REAL,
            reps INTEGER,
            sets INTEGER,

            FOREIGN KEY(activity_id) 
            REFERENCES weightlifting(activity_id) ON DELETE CASCADE
        )
    """
    )

def row_to_model(row: tuple, user_name: str) -> Weightlifting:
    return get_one_weightlifting_session(row[0], user_name)

def model_to_dict(weightlifting: Weightlifting) -> dict:
    return weightlifting.model_dump()

def get_all_weightlifting_sessions(user_name: str) -> list[Weightlifting]:
    qry = """
        SELECT activity_id 
        FROM weightlifting
        where user_name=:user_name
    """
    params = {"user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row, user_name) for row in rows]

def get_exercises(activity_id: int) -> list[WeightliftingExercise]:
    qry = """
        SELECT 
            exercise, 
            weight, 
            reps, 
            sets 
        FROM weightlifting_exercises
        WHERE activity_id=:activity_id
    """
    params = {"activity_id": activity_id}
    rows = execute_qry(qry, params)
    return [
        WeightliftingExercise(
            exercise=row[0],
            weight=row[1],
            reps=row[2],
            sets=row[3]
        )
    for row in rows
    ]

def get_one_weightlifting_session(
        activity_id: int, 
        user_name: str
    ) -> Weightlifting:
    qry = """
        SELECT activity_id 
        FROM weightlifting 
        WHERE activity_id=:activity_id 
        AND user_name=:user_name
    """
    params = {"activity_id": activity_id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return Weightlifting(
            activity_id=row[0],
            exercises=get_exercises(activity_id)
        )
    raise Missing(msg="Weightlifting session does not exist")

def get_weightlifting_sessions_by_date(
        session_date: date, 
        user_name: str
    ) -> list[Weightlifting]:
    qry = """
        SELECT weightlifting.activity_id
        FROM weightlifting
        JOIN activity
        ON weightlifting.activity_id = activity.id
        Join daily_log
        ON activity.daily_log_id = daily_log.id
        WHERE daily_log.date=:session_date 
        AND weightlifting.user_name=:user_name
    """
    params = {"session_date": str(session_date), "user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row, user_name) for row in rows]

def create_weightlifting_session(
        weightlifting_session: Weightlifting, 
        user_name: str
    ) -> Weightlifting:
    if not weightlifting_session:
        raise ValueError("Weightlifting session cannot be empty")
    qry = """
        INSERT INTO weightlifting( 
            activity_id, 
            user_name
        )
        VALUES(
            :activity_id, 
            :user_name
        )
    """
    params = {
        "activity_id": weightlifting_session.activity_id, 
        "user_name": user_name
    }
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            for exercise in weightlifting_session.exercises:
                qry = """
                    INSERT INTO weightlifting_exercises(
                        activity_id, 
                        exercise, 
                        weight, 
                        reps, 
                        sets
                    )
                    VALUES(
                        :activity_id, 
                        :exercise, 
                        :weight, 
                        :reps, 
                        :sets
                    )
                """
                params = {
                    "activity_id": weightlifting_session.activity_id,
                    **exercise.model_dump()
                }
                curs.execute(qry, params)
            conn.commit()
    except IntegrityError:
        raise Duplicate(msg="Weightlifting session already exists")
    return get_one_weightlifting_session(
        weightlifting_session.activity_id, 
        user_name
    )

def modify_weightlifting_session(
        weightlifting_session: WeightliftingUpdate, 
        user_name: str
    ) -> Weightlifting:
    if not weightlifting_session:
        raise ValueError("Weightlifting session cannot be empty")
    update_qry = """
        UPDATE activity
        SET 
            description=:description, 
            duration=:duration
        WHERE id=:activity_id 
        AND user_name=:user_name
    """
    params = {
        "activity_id": weightlifting_session.activity_id,
        "description": weightlifting_session.description,
        "duration": weightlifting_session.duration,
        "user_name": user_name
    }
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(update_qry, params)
        if curs.rowcount != 1:
            raise Missing(msg="Weightlifting session does not exist")
        delete_qry = """
            DELETE FROM weightlifting_exercises
            WHERE activity_id=:activity_id
        """
        delete_params = {"activity_id": weightlifting_session.activity_id}
        curs.execute(delete_qry, delete_params)
        insert_qry = """
            INSERT INTO weightlifting_exercises(
                activity_id, 
                exercise, 
                weight, 
                reps, 
                sets
            )
            VALUES(
                :activity_id, 
                :exercise, 
                :weight, 
                :reps, 
                :sets
            )
        """
        for exercise in weightlifting_session.exercises:
            params = {
                "activity_id": weightlifting_session.activity_id,
                **exercise.model_dump()
            }
            curs.execute(insert_qry, params)
        conn.commit()
    return get_one_weightlifting_session(
        weightlifting_session.activity_id, 
        user_name
    )