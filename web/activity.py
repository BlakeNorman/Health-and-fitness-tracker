from fastapi import APIRouter, HTTPException, Depends

from models.activity import Activity, ActivityIn, ActivityUpdate
from models.errors import Duplicate, Missing
from models.user import User
from web.user import get_current_user

import service.activity as activity_service
 
from datetime import date
  
router = APIRouter(prefix="/activity")  

##########################################################
# Graph Functions
##########################################################

@router.get("/activity-durations-graph")
def get_durations(
        current_user: User = Depends(get_current_user), 
        range: str = "all", 
        date: str | None = None, 
        category: str = "all"
    ):
    durations = activity_service.get_durations(
        current_user.name, 
        range=range, 
        date=date, 
        category=category
    )
    if not durations:
        raise HTTPException(
            status_code=404, 
            detail="No activity data for this period"
        )
    return {"durations": durations, "range": range, "date": date}

@router.get("/activity-distances-graph")
def get_distances(
        current_user: User = Depends(get_current_user), 
        range: str = "all", 
        date: str | None = None, 
        category: str = "all",
        graph_type: str = "standard"
    ):
    if graph_type == "standard":
        distances = activity_service.get_distances( 
            current_user.name, 
            range=range, 
            date=date,
            category=category
        )   
    elif graph_type == "cumulative":
        distances = activity_service.get_cumulative_distances(
            current_user.name, 
            range=range, 
            date=date,
            category=category
        )
    if not distances:
        raise HTTPException(
            status_code=404, 
            detail="No activity data for this period"
        )
    return {
        "distances": distances, 
        "range": range, 
        "date": date
    }

@router.get("/activity-paces-graph")
def activity_paces_graph(
        current_user: User = Depends(get_current_user), 
        range: str = "all", 
        date: str | None = None,
        category: str = "all"
    ):
    paces = activity_service.get_paces(
        current_user.name, 
        range=range, 
        date=date, 
        category=category
    )
    if not paces:
        raise HTTPException(
            status_code=404, 
            detail="No activity data for this period"
        )
    return {
        "paces": paces, 
        "range": range, 
        "date": date
    }

##########################################################
# Activity Log Functions
##########################################################

@router.get("/")
def get_all_activities(
        current_user: User = Depends(get_current_user)
    ) -> list[Activity]:
    return activity_service.get_all_activities(current_user.name)

@router.get("/date/{activity_date}")
def get_activities_by_date(
        activity_date: date, 
        current_user: User = Depends(get_current_user)
    ) -> list[Activity]:
    return activity_service.get_activities_by_date(
        activity_date, 
        current_user.name
    )
   
@router.get("/{id}") 
def get_one_activity(
        id: int, 
        current_user: 
        User = Depends(get_current_user)
    ) -> Activity:
    try:
        return activity_service.get_one_activity(
            id, 
            current_user.name
        ) 
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.post("/", status_code=201)
def create_activity(
        activity: ActivityIn, 
        current_user: User = Depends(get_current_user)
    ) -> Activity:
    try:
        return activity_service.create_activity(
            activity, 
            current_user.name
        )
    except Duplicate as exc:
        raise HTTPException(status_code=409, detail=exc.msg)

@router.patch("/")
def modify_activity(
        activity: ActivityUpdate, 
        current_user: User = Depends(get_current_user)
    ) -> Activity:
    try:
        return activity_service.modify_activity(
            activity, 
            current_user.name
        )
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)

@router.delete("/{id}")
def delete_activity(
        id: int, 
        current_user: User = Depends(get_current_user)
    ) -> None:
    try:
        return activity_service.delete_activity(id, current_user.name)
    except Missing as exc:
        raise HTTPException(status_code=404, detail=exc.msg)