from .init import get_db, execute_qry, execute_qry_one
from models.health import Health, FoodConsumed, HealthUpdate
from models.errors import Duplicate, Missing
from data.daily_log import delete_if_empty

from sqlite3 import IntegrityError
from datetime import date, time

# Create health table and foods_consumed table
with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS health(
            id INTEGER PRIMARY KEY,
            user_name TEXT NOT NULL,
            daily_log_id INTEGER NOT NULL UNIQUE,
            notes TEXT,

            nutrition_calculation TEXT NOT NULL DEFAULT 'manual',

            calories REAL,
            fats REAL,
            carbs REAL,
            protein REAL,

            water REAL,
            weight REAL,
            bedtime TEXT,
            wake_time TEXT,

            FOREIGN KEY(user_name) REFERENCES user(name),
            FOREIGN KEY(daily_log_id) REFERENCES daily_log(id) ON DELETE CASCADE
        )
    """
    )
with get_db() as conn:
    curs = conn.cursor()
    curs.execute(
        """
        CREATE TABLE IF NOT EXISTS foods_consumed(
            id INTEGER PRIMARY KEY,
            health_id INTEGER NOT NULL,
            food TEXT,
            calories REAL,
            fats REAL,
            carbs REAL,
            protein REAL,

            FOREIGN KEY(health_id) REFERENCES health(id) ON DELETE CASCADE
        )
    """
    )

# Find a row in the health table, use the information in that row to 
# build a Health object, return the Health object
def row_to_model(row):
    return Health(
        id=row[0],
        daily_log_id=row[2],
        notes=row[3],

        nutrition_calculation=row[4],

        calories=row[5],
        fats=row[6],
        carbs=row[7],
        protein=row[8],

        water=row[9],
        weight=row[10],
        bedtime=time.fromisoformat(row[11]) if row[11] else None,
        wake_time=time.fromisoformat(row[12]) if row[12] else None,

        log_date=row[13],

        foods=get_foods_consumed(row[0]),
    )

# Take in a Health object, convert its information into a dictionary 
# but exclude foods and id, return the dictionary
def model_to_dict(health_log: Health) -> dict:
    return health_log.model_dump(exclude={"foods", "id"})

# Take in a HealthUpdate object and convert its information to a dictionary
# but exclude foods, return the dictionary
def update_model_to_dict(health_log: HealthUpdate) -> dict:
    return health_log.model_dump(exclude={"foods"})

# For each row in the health table, gather the information in each column
# then gather the date in the daily_log table which has the same id
# as the current health table row, and convert that information into a Health object.
# Return a list of all the newly created Health objects.
def get_all_health_logs(user_name: str) -> list[Health]:
    qry = """
        SELECT 
            health.*, 
            daily_log.date 
        FROM health
        JOIN daily_log
        ON health.daily_log_id = daily_log.id
        WHERE user_name=:user_name
    """
    params = {"user_name": user_name}
    rows = execute_qry(qry, params)
    return [row_to_model(row) for row in rows]

# Take in an id, find the rows in the foods_consumed table with that id,
# and gather the information from prescribed columns in each row.
# Use the gathered info from each row to constuct a FoodConsumed object
# and return a list of all newly constructed FoodConsumed objects.
def get_foods_consumed(health_id: int) -> list[FoodConsumed]:
    qry = """
        SELECT 
            food, 
            calories, 
            fats, 
            carbs, 
            protein 
        FROM foods_consumed
        WHERE health_id=:health_id
    """
    params = {"health_id": health_id}
    rows = execute_qry(qry, params)
    return [FoodConsumed(
        food=row[0],
        calories=row[1],
        fats=row[2],
        carbs=row[3],
        protein=row[4]
        ) 
        for row in rows
    ]

# Find the row in the health table with the input id and find 
# the date in the row of the daily_log table whose id matches 
# the health row's daily_log_id. 
# Convert the gathered information to a Health object 
# and return the Health object.
def get_one_health_log(id: int, user_name: str) -> Health:
    qry = """
        SELECT 
            health.*, 
            daily_log.date 
        FROM health 
        JOIN daily_log
        ON health.daily_log_id = daily_log.id
        WHERE health.id=:id 
        AND health.user_name=:user_name
    """
    params = {"id": id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return row_to_model(row)
    raise Missing(msg="Health log does not exist")

# Select the id from the health table row where the input log_date is in 
# the row of the daily_log table with the id which is the same as the 
# health row's daily_log_id. 
# Return the health log with the id.
def get_health_log_by_date(log_date: date, user_name: str) -> Health: 
    qry = """
        SELECT health.id
        FROM health
        JOIN daily_log
        ON health.daily_log_id = daily_log.id
        WHERE daily_log.date=:log_date 
        AND health.user_name=:user_name
    """
    params = {"log_date": str(log_date), "user_name": user_name}
    row = execute_qry_one(qry, params)
    if row:
        return get_one_health_log(row[0], user_name)
    raise Missing(msg="Health log does not exist")

# Take in a Health object and use the information in the Health object 
# to create a new row in the health table and the foods_consumed table
def create_health_log(health_log: Health, user_name: str) -> Health:
    if not health_log:
        raise ValueError("Health log cannot be empty")
    qry = """
        INSERT INTO health(
            user_name, 
            daily_log_id, 
            notes, 

            nutrition_calculation,

            calories, 
            fats, 
            carbs, 
            protein, 

            water, 
            weight, 
            bedtime, 
            wake_time
        )
        VALUES(
            :user_name, 
            :daily_log_id, 
            :notes, 

            :nutrition_calculation,

            :calories, 
            :fats, 
            :carbs, 
            :protein, 

            :water, 
            :weight, 
            :bedtime, 
            :wake_time
        )
    """
    params = model_to_dict(health_log)
    params["user_name"] = user_name
    params["bedtime"] = (
        health_log.bedtime.isoformat() if health_log.bedtime else None
    )
    params["wake_time"] = (
        health_log.wake_time.isoformat() if health_log.wake_time else None
    )
    try:
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            health_id = curs.lastrowid
            for food in health_log.foods:
                qry = """
                    INSERT INTO foods_consumed(
                        health_id, 
                        food, calories, 
                        fats, 
                        carbs, 
                        protein
                    )
                    VALUES(
                        :health_id, 
                        :food, 
                        :calories, 
                        :fats, 
                        :carbs, 
                        :protein
                    )
                """
                params = {
                    "health_id": health_id,
                    **food.model_dump()
                }
                curs.execute(qry, params)
            conn.commit()
    except IntegrityError:
        raise Duplicate(msg="Health log already exists")
    return get_one_health_log(health_id, user_name)

# Take in a HealthUpdate object. If no fields are being provided by the healthUpdate
# object, then return an error. 
# Create a dictionary from the HealthUpdate object.
# The health update object does not have an id or username, so they need to be
# added to the dictionary created from the HealthUpdate object.
# If bedtime and/or wake_time are provided by the HealthUpdate object, then 
# convert them to iso format. 
# For each field in params other than id and username, associate that field with 
# the update value. Then connect to the database and have it make these updates 
# in the health table. 
# If foods were provided, delete the foods currently in foods_consumed and 
# replace them with the provided foods. 
def modify_health_log(
        id: int, 
        health_log: HealthUpdate, 
        user_name: str
    ) -> Health:
    if not health_log.model_fields_set:
        raise ValueError("Health log cannot be empty")
    params = update_model_to_dict(health_log)
    params["id"] = id
    params["user_name"] = user_name
    if "bedtime" in params:
        params["bedtime"] = (
            health_log.bedtime.isoformat() 
            if health_log.bedtime is not None 
            else None
        )
    if "wake_time" in params:
        params["wake_time"] = (
            health_log.wake_time.isoformat() 
            if health_log.wake_time is not None 
            else None
        )
    fields = []
    for field in params:
        if field not in {"id", "user_name"}:
            fields.append(f"{field}=:{field}")
    if fields:
        qry = f"""
            UPDATE health
            SET {", ".join(fields)}
            WHERE id=:id
            AND user_name=:user_name
        """
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            if curs.rowcount != 1:
                raise Missing(msg="Health log does not exist")
            conn.commit()
    else:
        qry = """
            SELECT id
            FROM health
            WHERE id=:id
            AND user_name=:user_name
        """
        row = execute_qry_one(qry, {"id": id, "user_name": user_name})
        if not row:
            raise Missing(msg="Health log does not exist")
    if health_log.foods is not None:
        qry = """
            DELETE FROM foods_consumed 
            WHERE health_id=:health_id
        """
        params = {"health_id": id}
        with get_db() as conn:
            curs = conn.cursor()
            curs.execute(qry, params)
            for food in health_log.foods:
                qry = """
                    INSERT INTO foods_consumed(
                        health_id, 
                        food, 
                        calories, 
                        fats, 
                        carbs, 
                        protein
                    )
                    VALUES(
                        :health_id, 
                        :food, 
                        :calories, 
                        :fats, 
                        :carbs, 
                        :protein
                    )
                """
                params = {"health_id": id, **food.model_dump()}
                curs.execute(qry, params)
            conn.commit()
    return get_one_health_log(id, user_name)

# Find the row in the health table which has the input id and username, 
# then return the daily_log_id from that row or throw an error if it does not exist.
# Delete the row in the health table containing the input id and username
def delete_health_log(id: int, user_name: str) -> None:
    qry = """
        SELECT daily_log_id 
        FROM health 
        WHERE id=:id 
        AND user_name=:user_name
    """
    params = {"id": id, "user_name": user_name}
    row = execute_qry_one(qry, params)
    if not row:
        raise Missing(msg="Health log does not exist")
    daily_log_id = row[0]
    qry = """
        DELETE FROM health 
        WHERE id=:id 
        AND user_name=:user_name
    """
    with get_db() as conn:
        curs = conn.cursor()
        curs.execute(qry, params)
        conn.commit()
    delete_if_empty(daily_log_id, user_name)


#########################################
# Graph functions
#########################################


ALLOWED_PARAMETERS = {
    "calories",
    "water",
    "weight"
}

# Find the rows in the health table that have the input username, 
# then for each row in health, find the rows in the daily_log table 
# which have id equal to health.daily_log_id. 
# From the health rows, select the information in the parameter column
# and from the corresponding daily_log rows, select the date.
# Return this information ordered by date. 
def get_health_parameter(parameter: str, user_name: str):
    if parameter not in ALLOWED_PARAMETERS:
        raise ValueError("Invalid parameter")
    qry = f"""
        SELECT 
            daily_log.date, 
            health.{parameter} 
        FROM health
        JOIN daily_log
        ON health.daily_log_id = daily_log.id
        WHERE health.user_name=:user_name
        ORDER BY daily_log.date
    """ 
    params = {"user_name": user_name}
    return execute_qry(qry, params)

# From all health table rows select fats, carbs, protein and from the 
# daily_log rows associated by id=daily_log_id, select the date
# return this info sorted by date
def get_macros(user_name: str):
    qry = """
        SELECT 
            daily_log.date, 
            health.fats, 
            health.carbs, 
            health.protein 
        FROM health
        JOIN daily_log
        ON health.daily_log_id = daily_log.id
        WHERE health.user_name=:user_name
        ORDER BY daily_log.date
    """ 
    params = {"user_name": user_name}
    return execute_qry(qry, params)

# Similar to get_macros
def get_sleep_data(user_name: str):
    qry = """
        SELECT 
            daily_log.date, 
            health.bedtime, 
            health.wake_time 
        FROM health
        JOIN daily_log
        ON health.daily_log_id = daily_log.id
        WHERE health.user_name=:user_name
        ORDER BY daily_log.date
    """ 
    params = {"user_name": user_name}
    return execute_qry(qry, params)