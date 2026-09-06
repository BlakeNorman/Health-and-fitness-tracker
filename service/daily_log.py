import data.daily_log as data
from models.daily_log import DailyLog

from datetime import date

def get_all_logs(user_name: str) -> list[DailyLog]:
    return data.get_all_logs(user_name)

def get_one_log(id: int, user_name: str) -> DailyLog | None:
    return data.get_one_log(id, user_name)

def get_log_by_date(log_date: date, user_name: str) -> DailyLog:
    return data.get_log_by_date(log_date, user_name)

def create_log(log: DailyLog, user_name: str) -> DailyLog:
    return data.create_log(log, user_name)

def modify_log(log: DailyLog, user_name: str) -> DailyLog:
    return data.modify_log(log, user_name)

def delete_log(id: int, user_name: str) -> None:
    return data.delete_log(id, user_name)