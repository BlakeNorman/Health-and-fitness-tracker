import data.running as running_data

from models.running import Run, RunCreate, RunUpdate
from models.activity import ActivityIn, ActivityUpdate
from models.daily_log import DailyLogIn
from models.errors import Missing

import service.daily_log as daily_log_service
import service.activity as activity_service

from datetime import date

def get_all_runs(user_name: str) -> list[Run]:
    return running_data.get_all_runs(user_name)

def get_one_run(activity_id: int, user_name: str) -> Run:
    return running_data.get_one_run(activity_id, user_name)

def get_runs_by_date(run_date: date, user_name: str) -> list[Run]:
    return running_data.get_runs_by_date(run_date, user_name)

def create_run(run: RunCreate, user_name: str) -> Run:
    try:
        log = daily_log_service.get_log_by_date(run.log_date, user_name)
    except Missing:
        log = daily_log_service.create_log(
            DailyLogIn(date=run.log_date), user_name
        )
 
    activity = activity_service.create_activity(
        ActivityIn(
        daily_log_id=log.id, 
        category="Running", 
        description=run.description, 
        duration=run.duration
        ),
        user_name
    )

    new_run = Run(
        activity_id=activity.id,
        distance=run.distance,
        pace=run.pace
        )
    
    return running_data.create_run(new_run, user_name)

def modify_run(run: RunUpdate, user_name: str) -> Run:
    activity_service.modify_activity(
        ActivityUpdate(
            id=run.activity_id,
            description=run.description,
            duration=run.duration
        ),
        user_name
    )
    return running_data.modify_run(
        Run(
            activity_id=run.activity_id,
            distance=run.distance,
            pace=run.pace
        ),
        user_name
    )

def delete_run(activity_id: int, user_name: str) -> None:
    return activity_service.delete_activity(activity_id, user_name)