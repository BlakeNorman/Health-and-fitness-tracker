from .init import get_db, execute_qry, execute_qry_one
from models.health import Health, FoodConsumed, HealthUpdate
from models.errors import Duplicate, Missing
from data.daily_log import delete_if_empty

from sqlite3 import IntegrityError
from datetime import date, time

# health table
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
# foods_consumed table
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

def model_to_dict(health_log: Health) -> dict:
    return health_log.model_dump(exclude={"foods", "id"})

def update_model_to_dict(health_log: HealthUpdate) -> dict:
    return health_log.model_dump(exclude={"foods"})

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