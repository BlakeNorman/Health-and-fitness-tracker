from fastapi import APIRouter, HTTPException, Depends

from models.weightlifting import Weightlifting, WeightliftingCreate, WeightliftingUpdate
from models.errors import Missing, Duplicate
from models.user import User

from web.user import get_current_user

import service.weightlifting as weightlifting_service
 
from datetime import date

router = APIRouter(prefix="/weightlifting")

@router.get("/")   
def get_all_weightlifting_sessions(
        current_user: User = Depends(get_current_user)
    ) -> list[Weightlifting]:
    return weightlifting_service.get_all_weightlifting_sessions(
        current_user.name
    )

@router.get("/date/{weightlifting_session_date}")
def get_weightlifting_sessions_by_date(
        weightlifting_session_date: date,
        current_user: User = Depends(get_current_user)
    ) -> list[Weightlifting]:
    return weightlifting_service.get_weightlifting_sessions_by_date(
        weightlifting_session_date, 
        current_user.name
    )

@router.get("/{activity_id}")
def get_one_weightlifting_session(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> Weightlifting:
    try:
        return weightlifting_service.get_one_weightlifting_session(
            activity_id, 
            current_user.name
        )
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201)
def create_weightlifting_session(
        weightlifting_session: WeightliftingCreate, 
        current_user: User = Depends(get_current_user)
    ) -> Weightlifting:
    try:
        return weightlifting_service.create_weightlifting_session(
            weightlifting_session, 
            current_user.name
        )
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/")
def modify_weightlifting_session(
        weightlifting_session: WeightliftingUpdate, 
        current_user: User = Depends(get_current_user)
    ) -> Weightlifting:
    try:
        return weightlifting_service.modify_weightlifting_session(
            weightlifting_session, 
            current_user.name
        )
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{activity_id}")
def delete_weightlifting_session(
        activity_id: int, 
        current_user: User = Depends(get_current_user)
    ) -> None:
    try:
        return weightlifting_service.delete_weightlifting_session(
            activity_id, 
            current_user.name
        )
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
