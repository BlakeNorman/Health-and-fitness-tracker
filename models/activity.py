from pydantic import BaseModel
from datetime import date

class ActivityIn(BaseModel):
    daily_log_id: int
    category: str
    description: str = ""
    duration: float

class Activity(ActivityIn):
    id: int
    log_date: date

class ActivityUpdate(BaseModel):
    id: int
    description: str = ""
    duration: float