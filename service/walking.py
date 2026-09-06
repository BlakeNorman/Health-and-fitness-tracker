import data.walking as walking_data

from models.walking import Walk, WalkCreate, WalkUpdate
from models.activity import ActivityIn, ActivityUpdate
from models.daily_log import DailyLogIn
from models.errors import Missing

import service.daily_log as daily_log_service
import service.activity as activity_service

from datetime import date

def get_all_walks(user_name: str) -> list[Walk]:
    return walking_data.get_all_walks(user_name)

def get_one_walk(activity_id: int, user_name: str) -> Walk:
    return walking_data.get_one_walk(activity_id, user_name)

def get_walks_by_date(walk_date: date, user_name: str) -> list[Walk]:
    return walking_data.get_walks_by_date(walk_date, user_name)

def create_walk(walk: WalkCreate, user_name: str) -> Walk:
    try:
        log = daily_log_service.get_log_by_date(walk.log_date, user_name)
    except Missing:
        log = daily_log_service.create_log(
            DailyLogIn(date=walk.log_date), user_name
        )
    activity = activity_service.create_activity(
        ActivityIn(
            daily_log_id=log.id, 
            category="Walking", 
            description=walk.description, 
            duration=walk.duration
        ),
        user_name
    )
    new_walk = Walk(
        activity_id=activity.id,
        distance=walk.distance,
        pace=walk.pace
    )
    return walking_data.create_walk(new_walk, user_name)

def modify_walk(walk: WalkUpdate, user_name: str) -> Walk:
    activity_service.modify_activity(
        ActivityUpdate(
            id=walk.activity_id,
            description=walk.description,
            duration=walk.duration
        ),
        user_name
    )
    return walking_data.modify_walk(
        Walk(
            activity_id=walk.activity_id,
            distance=walk.distance,
            pace=walk.pace
        ),
        user_name
    )

def delete_walk(activity_id: int, user_name: str) -> None:
    return activity_service.delete_activity(activity_id, user_name)