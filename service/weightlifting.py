import data.weightlifting as weightlifting_data

from models.weightlifting import Weightlifting, WeightliftingCreate, WeightliftingUpdate
from models.activity import ActivityIn
from models.daily_log import DailyLogIn
from models.errors import Missing

import service.daily_log as daily_log_service
import service.activity as activity_service

from datetime import date

def get_all_weightlifting_sessions(
        user_name: str
    ) -> list[Weightlifting]:
    return weightlifting_data.get_all_weightlifting_sessions(user_name)

def get_one_weightlifting_session(
        activity_id: int, 
        user_name: str
    ) -> Weightlifting:
    return weightlifting_data.get_one_weightlifting_session(
        activity_id, 
        user_name
    )

def get_weightlifting_sessions_by_date(
        weightlifting_session_date: date, 
        user_name: str
    ) -> list[Weightlifting]:
    return weightlifting_data.get_weightlifting_sessions_by_date(
        weightlifting_session_date, 
        user_name
    )

def create_weightlifting_session(
        weightlifting_session: WeightliftingCreate, 
        user_name: str
    ) -> Weightlifting:
    try:
        log = daily_log_service.get_log_by_date(
            weightlifting_session.log_date, 
            user_name
        )
    except Missing:
        log = daily_log_service.create_log(
            DailyLogIn(date=weightlifting_session.log_date), 
            user_name
        )

    activity = activity_service.create_activity(
        ActivityIn(
        daily_log_id=log.id, 
        category="Weightlifting", 
        description=weightlifting_session.description,
        duration=weightlifting_session.duration        
        ),
        user_name
    ) 
  
    new_weightlifting_session = Weightlifting(
        activity_id=activity.id,
        exercises=weightlifting_session.exercises
        )
    
    return weightlifting_data.create_weightlifting_session(
        new_weightlifting_session, 
        user_name
    )

def modify_weightlifting_session(
        weightlifting_session: WeightliftingUpdate, 
        user_name: str
    ) -> Weightlifting:
    return weightlifting_data.modify_weightlifting_session(
        weightlifting_session, 
        user_name
    )

def delete_weightlifting_session(
        activity_id: int, 
        user_name: str
    ) -> None:
    return activity_service.delete_activity(
        activity_id, 
        user_name
    )