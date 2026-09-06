import data.cycling as cycling_data

from models.cycling import Cycle, CycleCreate, CycleUpdate
from models.activity import ActivityIn, ActivityUpdate
from models.daily_log import DailyLogIn
from models.errors import Missing

import service.daily_log as daily_log_service
import service.activity as activity_service

from datetime import date

def get_all_cycles(user_name: str) -> list[Cycle]:
    return cycling_data.get_all_cycles(user_name)

def get_one_cycle(activity_id: int, user_name: str) -> Cycle:
    return cycling_data.get_one_cycle(activity_id, user_name)

def get_cycles_by_date(cycle_date: date, user_name: str) -> list[Cycle]:
    return cycling_data.get_cycles_by_date(cycle_date, user_name)

def create_cycle(cycle: CycleCreate, user_name: str) -> Cycle:
    try:
        log = daily_log_service.get_log_by_date(cycle.log_date, user_name)
    except Missing:
        log = daily_log_service.create_log(
            DailyLogIn(date=cycle.log_date), user_name
        )
    activity = activity_service.create_activity(
        ActivityIn(
            daily_log_id=log.id, 
            category="Cycling", 
            description=cycle.description, 
            duration=cycle.duration
        ),
        user_name
    )
    new_cycle = Cycle(
        activity_id=activity.id,
        distance=cycle.distance,
        pace=cycle.pace
    )
    return cycling_data.create_cycle(new_cycle, user_name)

def modify_cycle(cycle: CycleUpdate, user_name: str) -> Cycle:
    activity_service.modify_activity(
        ActivityUpdate(
            id=cycle.activity_id,
            description=cycle.description,
            duration=cycle.duration
        ),
        user_name
    )
    return cycling_data.modify_cycle(
        Cycle(
            activity_id=cycle.activity_id,
            distance=cycle.distance,
            pace=cycle.pace
        ),
        user_name
    )

def delete_cycle(activity_id: int, user_name: str) -> None:
    return activity_service.delete_activity(activity_id, user_name)