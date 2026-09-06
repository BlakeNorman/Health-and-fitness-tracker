import data.activity as activity_data
from models.activity import Activity, ActivityIn, ActivityUpdate

from datetime import date

def get_all_activities(user_name: str) -> list[Activity]:
    return activity_data.get_all_activities(user_name)

def get_one_activity(id: int, user_name: str) -> Activity | None:
    return activity_data.get_one_activity(id, user_name)

def get_activities_by_date(activity_date: date, user_name: str) -> list[Activity]:
    return activity_data.get_activities_by_date(activity_date, user_name)

def create_activity(activity: ActivityIn, user_name: str) -> Activity:
    return activity_data.create_activity(activity, user_name)

def modify_activity(activity: ActivityUpdate, user_name: str) -> Activity:
    return activity_data.modify_activity(activity, user_name)

def delete_activity(id: int, user_name: str) -> None:
    return activity_data.delete_activity(id, user_name)

#############################################
# Activity Graph Functions
#############################################

def get_durations(
        user_name: str, 
        range: str = "all", 
        date: str | None = None, 
        category: str = "all"
    ):
    rows = activity_data.get_all_durations(user_name)
    durations = [
        {
            "date": row[0], 
            "duration": row[1], 
            "category": row[2]
        } 
        for row in rows
    ]
    if category != "all":
        durations = [
            item for item in durations if item["category"] == category
        ]
    if range == "year":
        durations = [
            item for item in durations if item["date"].startswith(date[:4])
        ]
    elif range == "month":
        durations = [
            item for item in durations if item["date"].startswith(date[:7])
        ]
    return durations

def get_distances(
        user_name: str, 
        range: str = "all", 
        date: str | None = None, 
        category: str = "all"
    ):
    rows = activity_data.get_all_distances(user_name)
    distances = [
        {
            "date": row[0], 
            "category": row[1], 
            "distance": row[2]
        } 
        for row in rows if row[2] is not None
    ]
    if category != "all":
        distances = [
            item for item in distances if item["category"] == category
        ]
    if range == "year":
        distances = [
            item for item in distances if item["date"].startswith(date[:4])
        ]
    elif range == "month":
        distances = [
            item for item in distances if item["date"].startswith(date[:7])
        ]
    return distances

def get_cumulative_distances(
        user_name: str, 
        range: str = "all", 
        date: str | None = None, 
        category: str = "all"
    ):
    distances = get_distances(
        user_name, 
        range=range, 
        date=date, 
        category=category
    )
    cumulative = 0
    result = []
    for item in distances:
        cumulative += item["distance"]
        result.append({"date": item["date"], "distance": cumulative})
    return result

def get_paces(
        user_name: str, 
        range: str = "all", 
        date: str | None = None, 
        category: str = "all"
    ):
    rows = activity_data.get_all_pace_data(user_name)
    data = [
        {
            "date": row[0], 
            "category": row[1], 
            "duration": row[2], 
            "distance": row[3]
        } 
        for row in rows if row[3] is not None and row[3] > 0
    ]
    if category != "all":
        data = [
            item for item in data if item["category"] == category
        ]
    if range == "year":
        data = [
            item for item in data if item["date"].startswith(date[:4])
        ]
    elif range == "month":
        data = [
            item for item in data if item["date"].startswith(date[:7])
        ]
    paces = [
        {
            "date": item["date"], 
            "category": item["category"], 
            "pace": item["duration"] / item["distance"]
        } for item in data
    ]
    return paces