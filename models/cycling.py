from pydantic import BaseModel

from datetime import date

class Cycle(BaseModel):
    activity_id: int
    distance: float     
    pace: float  

class CycleCreate(BaseModel):
    log_date: date
    description: str = ""
    duration: int
    distance: float
    pace: float      

class CycleUpdate(BaseModel):
    activity_id: int
    description: str = ""
    duration: int
    distance: float
    pace: float