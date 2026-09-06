from pydantic import BaseModel

from datetime import date

class Run(BaseModel):
    activity_id: int
    distance: float     
    pace: float  

class RunCreate(BaseModel):
    log_date: date
    description: str = ""
    duration: int
    distance: float
    pace: float      

class RunUpdate(BaseModel):
    activity_id: int
    description: str = ""
    duration: int
    distance: float
    pace: float