from pydantic import BaseModel
from datetime import date

class DailyLogIn(BaseModel):
    date: date

class DailyLog(DailyLogIn):
    id: int