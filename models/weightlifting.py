from pydantic import BaseModel

from datetime import date

class WeightliftingExercise(BaseModel):
    exercise: str
    weight: float
    reps: int
    sets: int

class Weightlifting(BaseModel):
    activity_id: int
    exercises: list[WeightliftingExercise]

class WeightliftingCreate(BaseModel):
    log_date: date
    description: str = ""
    duration: float
    exercises: list[WeightliftingExercise]

class WeightliftingUpdate(BaseModel):
    activity_id: int
    description: str = ""
    duration: float
    exercises: list[WeightliftingExercise]

