from fastapi import APIRouter, HTTPException, Depends

from models.cycling import Cycle, CycleCreate, CycleUpdate
from models.errors import Missing, Duplicate
from models.user import User

from web.user import get_current_user

import service.cycling as cycling_service

from datetime import date

router = APIRouter(prefix="/cycling") 

@router.get("/") 
def get_all_cycles(
        current_user: User = Depends(get_current_user)
    ) -> list[Cycle]:
    return cycling_service.get_all_cycles(current_user.name)

@router.get("/date/{cycle_date}")
def get_cycles_by_date(
        cycle_date: date, 
        current_user: User = Depends(get_current_user)
    ) -> list[Cycle]:
    return cycling_service.get_cycles_by_date(
        cycle_date, 
        current_user.name
    )

@router.get("/{activity_id}")
def get_one_cycle(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> Cycle:
    try:
        return cycling_service.get_one_cycle(activity_id, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201)
def create_cycle(
        cycle: CycleCreate, 
        current_user: User = Depends(get_current_user)
    ) -> Cycle: 
    try:
        return cycling_service.create_cycle(cycle, current_user.name)
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/")
def modify_cycle(
        cycle: CycleUpdate, 
        current_user: User = Depends(get_current_user)
    ) -> Cycle:
    try:
        return cycling_service.modify_cycle(cycle, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{activity_id}")
def delete_cycle(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> None:
    try:
        return cycling_service.delete_cycle(activity_id, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
