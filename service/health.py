import data.health as health_data

from models.health import Health, HealthCreate, HealthUpdate, FoodConsumed
from models.daily_log import DailyLogIn
from models.errors import Missing

import service.daily_log as daily_log_service

from datetime import date

def get_all_health_logs(user_name: str) -> list[Health]:
    return health_data.get_all_health_logs(user_name)

def get_one_health_log(id: int, user_name: str) -> Health:
    return health_data.get_one_health_log(id, user_name)

def get_health_log_by_date(log_date: date, user_name: str) -> Health:
    return health_data.get_health_log_by_date(log_date, user_name)

def create_health_log(health_log: HealthCreate, user_name: str) -> Health:
    try:
        log = daily_log_service.get_log_by_date(health_log.log_date, user_name)
    except Missing:
        log = daily_log_service.create_log(
            DailyLogIn(date=health_log.log_date), 
            user_name
        )
    calorie_and_macro_totals = calculate_calorie_and_macro_totals(health_log)
    new_health_log = Health(
        daily_log_id=log.id,
        log_date=health_log.log_date,
        notes=health_log.notes,
        nutrition_calculation=health_log.nutrition_calculation,
        calories=calorie_and_macro_totals["calories"],
        fats=calorie_and_macro_totals["fats"],
        carbs=calorie_and_macro_totals["carbs"],
        protein=calorie_and_macro_totals["protein"],
        water=health_log.water,
        weight=health_log.weight,
        bedtime=health_log.bedtime,
        wake_time=health_log.wake_time,
        foods=health_log.foods
    )
    return health_data.create_health_log(new_health_log, user_name)

def modify_health_log(
        id: int, 
        health_log: HealthUpdate, 
        user_name: str
    ) -> Health:
    existing = health_data.get_one_health_log(id, user_name)
    nutrition_calculation = (
        health_log.nutrition_calculation 
        if health_log.nutrition_calculation is not None 
        else existing.nutrition_calculation
    )
    foods = (
        health_log.foods if health_log.foods is not None else existing.foods
    )
    if nutrition_calculation == "manual":
        pass
    else:
        for food in foods:
            if food.calories is None:
                raise ValueError(
                    "Food based nutrition calculations require calories for all foods"
                )
        totals = calculate_food_based_calorie_and_macro_totals(foods) 
        health_log.calories=totals["calories"]
        health_log.fats=totals["fats"]
        health_log.carbs=totals["carbs"]
        health_log.protein=totals["protein"]
    return health_data.modify_health_log(id, health_log, user_name)

def delete_health_log(id: int, user_name: str) -> None:
    return health_data.delete_health_log(id, user_name)

#################################################
# Calculate Calorie and Macro Totals
#################################################

# Sum the calories, fats, carbs, and protein from each food in foods.
def calculate_food_based_calorie_and_macro_totals(
        foods: list[FoodConsumed]
    ) -> dict:
    return {
        "calories": sum(food.calories or 0 for food in foods),
        "fats": sum(food.fats or 0 for food in foods),
        "carbs": sum(food.carbs or 0 for food in foods),
        "protein": sum(food.protein or 0 for food in foods)
    }

def calculate_calorie_and_macro_totals(
        health_log: HealthCreate | HealthUpdate
    ) -> dict:
    if health_log.nutrition_calculation == "manual":
        return {
            "calories": health_log.calories,
            "fats": health_log.fats, 
            "carbs": health_log.carbs,
            "protein": health_log.protein
        }
    for food in health_log.foods:
        if food.calories is None:
            raise ValueError(
                "Food based nutrition calculations require calories for all foods"
            )
    return calculate_food_based_calorie_and_macro_totals(health_log.foods)

#################################################
# Health Graphs Functions
#################################################

def get_health_parameter(
        user_name: str, 
        parameter: str, 
        range: str = "all", 
        date: str | None = None
    ):
    rows = health_data.get_health_parameter(parameter, user_name)
    data = [
        {
            "date": row[0], 
            f"{parameter}": row[1]
        } 
        for row in rows
    ]
    if range == "year":
        data = [
            item for item in data if item["date"].startswith(date[:4])
        ]
    elif range == "month":
        data = [
            item for item in data if item["date"].startswith(date[:7])
        ]
    return data

def get_macros(
        user_name: str, 
        range: str = "all", 
        date: str | None = None
    ):
    rows = health_data.get_macros(user_name)
    data = [
        {
            "date": row[0], 
            "fats": row[1], 
            "carbs": row[2], 
            "protein": row[3]
        } 
        for row in rows
    ]
    if range == "year":
        data = [
            item for item in data if item["date"].startswith(date[:4])
        ]
    elif range == "month":
        data = [
            item for item in data if item["date"].startswith(date[:7])
        ]
    return data

def get_sleep_data(
        user_name: str, 
        range: str = "all", 
        date: str | None = None
    ):
    rows = health_data.get_sleep_data(user_name)
    data = [
        {
            "date": row[0], 
            "bedtime": row[1], 
            "wake_time": row[2]
        } 
            for row in rows
    ]
    if range == "year":
        data = [
            item for item in data if item["date"].startswith(date[:4])
        ]
    elif range == "month":
        data = [
            item for item in data if item["date"].startswith(date[:7])
        ]
    return data