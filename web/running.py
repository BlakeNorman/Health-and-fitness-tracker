from fastapi import APIRouter, HTTPException, Depends

from models.running import Run, RunCreate, RunUpdate
from models.errors import Missing, Duplicate
from models.user import User

from web.user import get_current_user

import service.running as running_service

from datetime import date

router = APIRouter(prefix="/running") 

@router.get("/") 
def get_all_runs(
        current_user: User = Depends(get_current_user)
    ) -> list[Run]:
    return running_service.get_all_runs(current_user.name)

@router.get("/date/{run_date}")
def get_runs_by_date(
        run_date: date, 
        current_user: User = Depends(get_current_user)
    ) -> list[Run]:
    return running_service.get_runs_by_date(
        run_date, 
        current_user.name
    )

@router.get("/{activity_id}")
def get_one_run(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> Run:
    try:
        return running_service.get_one_run(
            activity_id, 
            current_user.name
        )
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201)
def create_run(
        run: RunCreate, 
        current_user: User = Depends(get_current_user)
    ) -> Run: 
    try:
        return running_service.create_run(run, current_user.name)
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/")
def modify_run(
        run: RunUpdate, 
        current_user: User = Depends(get_current_user)
    ) -> Run:
    try:
        return running_service.modify_run(run, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{activity_id}")
def delete_run(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> None:
    try:
        return running_service.delete_run(activity_id, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
