from pydantic import BaseModel

from datetime import date

class Walk(BaseModel):
    activity_id: int
    distance: float     
    pace: float  

class WalkCreate(BaseModel):
    log_date: date
    description: str = ""
    duration: int
    distance: float
    pace: float      

class WalkUpdate(BaseModel):
    activity_id: int
    description: str = ""
    duration: int
    distance: float
    pace: float