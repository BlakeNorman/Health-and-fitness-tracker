from fastapi import APIRouter, HTTPException, Depends

from models.health import Health, HealthCreate, HealthUpdate
from models.errors import Missing, Duplicate
from models.user import User
from web.user import get_current_user

import service.health as health_service
 
from datetime import date

router = APIRouter(prefix="/health")

@router.get("/")   
def get_all_health_logs(
        current_user: User = Depends(get_current_user)
    ) -> list[Health]:
    return health_service.get_all_health_logs(current_user.name)

@router.get("/health-graph")
def health_graph(
        parameter: str, 
        range: str = "all", 
        date: str | None = None, 
        current_user: User = Depends(get_current_user)
    ):
    data = health_service.get_health_parameter(
        current_user.name, 
        parameter=parameter, 
        range=range, 
        date=date
    )
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No {parameter} data during this period"
        )
    return {
        "data": data, 
        "parameter": parameter, 
        "range": range, 
        "date": date
    }

@router.get("/macros-graph")
def macros_graph(
        current_user: User = Depends(get_current_user), 
        range: str = "all", 
        date: str | None = None
    ):
    data = health_service.get_macros(
        current_user.name, 
        range=range, 
        date=date
    )
    if not data:
        raise HTTPException(
            status_code=404, 
            detail="No macros data for this period"
        )
    return {
        "data": data, 
        "range": range, 
        "date": date
    }

@router.get("/sleep-graph")
def sleep_graph(
        current_user: User = Depends(get_current_user), 
        range: str = "all", 
        date: str | None = None
    ):
    data = health_service.get_sleep_data(
        current_user.name, 
        range=range, 
        date=date
    )
    if not data:
        raise HTTPException(
            status_code=404, 
            detail="Missing bedtime and/or wake time data for this period"
        )
    return {
        "data": data, 
        "range": range, 
        "date": date
    }

@router.get("/date/{health_log_date}")
def get_health_log_by_date(
        health_log_date: date, 
        current_user: User = Depends(get_current_user)
    ) -> Health:
    try:
        return health_service.get_health_log_by_date(
            health_log_date, 
            current_user.name
        )
    except Missing:
        raise HTTPException(
            status_code=404, 
            detail="Health log does not exist"
        )

@router.get("/{id}")    
def get_one_health_log(
        id: int, 
        current_user: User = Depends(get_current_user)
    ) -> Health:
    try:
        return health_service.get_one_health_log(
            id, 
            current_user.name
        )
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201)
def create_health_log(
        health_log: HealthCreate, 
        current_user: User = Depends(get_current_user)
    ) -> Health:
    try:
        return health_service.create_health_log(
            health_log, 
            current_user.name
        )
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/{id}")
def modify_health_log(
        id: int, 
        health_log: HealthUpdate, 
        current_user: User = Depends(get_current_user)
    ) -> Health:
    try:
        return health_service.modify_health_log(
            id, 
            health_log, 
            current_user.name
        )
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{id}")
def delete_health_log(
        id: int, 
        current_user: User = Depends(get_current_user)
    ) -> None:
    try:
        return health_service.delete_health_log(id, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
