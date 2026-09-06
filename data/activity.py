from .init import get_db, execute_qry, execute_qry_one
from models.activity import Activity, ActivityIn, ActivityUpdate
from models.errors import Duplicate, Missing
from data.daily_log import delete_if_empty

from sqlite3 import IntegrityError
from datetime import date

# Create the activity table unless it already exists
with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS activity(
        id INTEGER PRIMARY KEY,
        user_name TEXT NOT NULL,
        daily_log_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        duration REAL,

        FOREIGN KEY(user_name) REFERENCES user(name),
        FOREIGN KEY(daily_log_id) REFERENCES daily_log(id) ON DELETE CASCADE
        )
    """
    )

# Convert information in a row of the activity table join the daily_log table
# into an Activity object
def row_to_model(row: tuple) -> Activity:
    return Activity(
        id=row[0],
        daily_log_id=row[2],
        category=row[3],
        description=row[4],
        duration=row[5],
        log_date=row[6]
        )

# Convert an Activity or ActivityUpdate object into a dictionary
def model_to_dict(activity: Activity | ActivityUpdate) -> dict:
    return activity.model_dump()

# Join the activity and daily log tables by activity.daily_log_id = daily_log.id.
# Then grab the information in all columns of the activity table 
# and the date from the daily_log table.
# Using the gathered information, construct an Activity object.
# Return a list consisting of all constructed Activity objects.
def get_all_activities(user_name: str) -> list[Activity]:
    qry = """
        SELECT 
            activity.*, 
            daily_log.date
        FROM activity
        JOIN daily_log
        ON activity.daily_log_id = daily_log.id
        WHERE activity.user_name=:user_name
    """
    params = {"user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

# Join the activity and daily log tables by activity.daily_log_id = daily_log.id.
# Then grab the information in all columns of the activity table 
# and the date from the daily_log table where activity.id = (the input id).
# Using the gathered information, construct and return an Activity object.
def get_one_activity(id: int, user_name: str) -> Activity:
    qry = """
        SELECT 
            activity.*, 
            daily_log.date 
        FROM activity 
        JOIN daily_log
        ON activity.daily_log_id = daily_log.id
        WHERE activity.id=:id 
        AND activity.user_name=:user_name
    """
    params = {"id": id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    raise Missing(msg=f"Activity {id} does not exist")

# Join the activity and daily log tables by avticity.daily_log_id = daily_log.id.
# Then grab the information in all columns of the activity table 
# and the date from the daily_log table where daily_log.date = (the input date).
# Using the gathered information, construct an Activity object.
# Return a list consisting of all constructed Activity objects.
def get_activities_by_date(
        activity_date: date, 
        user_name: str
    ) -> list[Activity]:
    qry = """
        SELECT 
            activity.*, 
            daily_log.date 
        FROM activity 
        JOIN daily_log 
        ON activity.daily_log_id = daily_log.id 
        WHERE daily_log.date=:activity_date 
        AND activity.user_name=:user_name
    """
    params = {"activity_date": str(activity_date), "user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

# Take in an Activity or ActivityIn object and use the information in the object
# to create a new row of the activity table.
def create_activity(
        activity: Activity | ActivityIn, 
        user_name: str
    ) -> Activity:
    if not activity:
        raise ValueError("Activity cannot be empty")
    qry = """
        INSERT INTO activity(
            user_name, 
            daily_log_id, 
            category, 
            description, 
            duration
        )
        VALUES(
            :user_name, 
            :daily_log_id, 
            :category, 
            :description, 
            :duration
        )
    """
    params = {"user_name": user_name, **model_to_dict(activity)}
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            conn.commit()
            id = curs.lastrowid
    except IntegrityError:
        raise Duplicate(msg=f"Activity already exists")
    return get_one_activity(id, user_name)

# Update the description and duration of the row in the activity table whose
# id matches the id in the provided ActivityUpdate object
def modify_activity(
        activity: ActivityUpdate, 
        user_name: str
    ) -> Activity:
    if not activity:
        raise ValueError("Activity cannot be empty")
    qry = """
        UPDATE activity
        SET 
            description=:description, 
            duration=:duration
        WHERE id=:id 
        AND user_name=:user_name
    """
    params = {"user_name": user_name, **model_to_dict(activity)}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        conn.commit()
        if curs.rowcount == 1:
            return get_one_activity(activity.id, user_name)
    raise Missing(msg=f"Activity {activity.id} does not exist")

# First check that the activity table has a row containing the input id.
# Then delete the row of the activity table which has the input id. 
def delete_activity(id: int, user_name: str) -> None:
    qry = """
        SELECT daily_log_id 
        FROM activity 
        WHERE id=:id 
        AND user_name=:user_name
    """
    params = {"id": id, "user_name": user_name}
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        row = curs.fetchone()
        if not row:
            raise Missing(msg="Activity does not exist")
        daily_log_id = row[0]
        qry = """
            DELETE FROM activity 
            WHERE id=:id 
            AND user_name=:user_name
        """
        curs.execute(qry, params)
        conn.commit()
    delete_if_empty(daily_log_id, user_name)    


##################################################
# Graph Functions
##################################################

# Join the activity and daily_log tables by activity.daily_log_id = daily_log.id.
# Return a list of rows consisting of date, duration, category. 
def get_all_durations(user_name: str):
    qry = """
        SELECT 
            daily_log.date, 
            activity.duration, 
            activity.category
        FROM activity
        JOIN daily_log
        ON activity.daily_log_id = daily_log.id
        WHERE activity.user_name=:user_name
        ORDER BY daily_log.date
    """
    params = {"user_name": user_name}
    return execute_qry(qry, params)

# Join the activity, daily_log, running, walking, and cycling tables by 
# activity.daily_log_id = daily_log.id and run/walk/cycle.activity_id = activity.id.
# Return the date, category, and distance from each activity where the 
# distance is chosen from the appropiate table based on the activity category.
def get_all_distances(user_name: str):
    qry = """
        SELECT
            daily_log.date,
            activity.category,
            CASE
                WHEN activity.category = 'Running' THEN running.distance
                WHEN activity.category = 'Walking' THEN walking.distance
                WHEN activity.category = 'Cycling' THEN cycling.distance
            END AS distance
        FROM activity
        JOIN daily_log
            ON activity.daily_log_id = daily_log.id
        LEFT JOIN running
            ON running.activity_id = activity.id
        LEFT JOIN walking
            ON walking.activity_id = activity.id
        LEFT JOIN cycling
            ON cycling.activity_id = activity.id
        WHERE activity.user_name = :user_name
        ORDER BY daily_log.date
    """
    params = {"user_name": user_name}
    return execute_qry(qry, params)

# Join the activity, daily_log, running, walking, and cycling tables by 
# activity.daily_log_id = daily_log.id and run/walk/cycle.activity_id = activity.id.
# Return the date, category, distance, and duration from each activity where the 
# distance is chosen from the appropiate table based on the activity category.
def get_all_pace_data(user_name: str):
    qry = """
        SELECT
            daily_log.date,
            activity.category,
            activity.duration,
            CASE
                WHEN activity.category = 'Running' THEN running.distance
                WHEN activity.category = 'Walking' THEN walking.distance
                WHEN activity.category = 'Cycling' THEN cycling.distance
            END AS distance
        FROM activity
        JOIN daily_log
            ON activity.daily_log_id = daily_log.id
        LEFT JOIN running
            ON running.activity_id = activity.id
        LEFT JOIN walking
            ON walking.activity_id = activity.id
        LEFT JOIN cycling
            ON cycling.activity_id = activity.id
        WHERE activity.user_name = :user_name
        ORDER BY daily_log.date
    """
    params = {"user_name": user_name}
    return execute_qry(qry, params)