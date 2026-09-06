from fastapi import APIRouter, HTTPException, Depends

from models.walking import Walk, WalkCreate, WalkUpdate
from models.errors import Missing, Duplicate
from models.user import User

from web.user import get_current_user

import service.walking as walking_service

from datetime import date

router = APIRouter(prefix="/walking") 

@router.get("/") 
def get_all_walks(
        current_user: User = Depends(get_current_user)
    ) -> list[Walk]:
    return walking_service.get_all_walks(current_user.name)

@router.get("/date/{walk_date}")
def get_walks_by_date(
        walk_date: date, 
        current_user: User = Depends(get_current_user)
    ) -> list[Walk]:
    return walking_service.get_walks_by_date(walk_date, current_user.name)

@router.get("/{activity_id}")
def get_one_walk(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> Walk:
    try:
        return walking_service.get_one_walk(activity_id, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201)
def create_walk(
        walk: WalkCreate, 
        current_user: User = Depends(get_current_user)
    ) -> Walk: 
    try:
        return walking_service.create_walk(walk, current_user.name)
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/")
def modify_walk(
        walk: WalkUpdate, 
        current_user: User = Depends(get_current_user)
    ) -> Walk:
    try:
        return walking_service.modify_walk(walk, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{activity_id}")
def delete_walk(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> None:
    try:
        return walking_service.delete_walk(activity_id, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
