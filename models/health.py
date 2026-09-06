from pydantic import BaseModel, Field
from typing import Literal
from datetime import date, time

NutritionCalculation = Literal["manual", "food_based"]

class FoodConsumed(BaseModel):
    food: str
    calories: float | None = None
    fats: float | None = None
    carbs: float | None = None
    protein: float | None = None

class Health(BaseModel):
    id: int | None = None
    daily_log_id: int
    log_date: date
    notes: str = ""
    nutrition_calculation: NutritionCalculation = "manual"
    calories: float | None = None
    fats: float | None = None
    carbs: float | None = None
    protein: float | None = None
    water: float | None = None
    weight: float | None = None
    bedtime: time | None = None
    wake_time: time | None = None
    foods: list[FoodConsumed] = Field(default_factory=list)

class HealthCreate(BaseModel):
    log_date: date
    notes: str = ""
    nutrition_calculation: NutritionCalculation = "manual"
    calories: float | None = None
    fats: float | None = None
    carbs: float | None = None
    protein: float | None = None
    bedtime: time | None = None
    wake_time: time | None = None
    water: float | None = None
    weight: float | None = None
    foods: list[FoodConsumed] = Field(default_factory=list)

class HealthUpdate(BaseModel):
    notes: str | None = None
    nutrition_calculation: NutritionCalculation | None = None
    calories: float | None = None
    fats: float | None = None
    carbs: float | None = None
    protein: float | None = None
    water: float | None = None
    weight: float | None = None
    bedtime: time | None = None
    wake_time: time | None = None
    foods: list[FoodConsumed] | None = None