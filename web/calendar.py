from fastapi import APIRouter, Depends

from models.user import User
from web.user import get_current_user
from data.init import execute_qry

router = APIRouter() 

@router.get("/calendar-data/{year}")
def get_calendar_year(
        year: int, 
        current_user: User = Depends(get_current_user)
    ):
    qry = """
        SELECT daily_log.date,
        EXISTS (
            SELECT 1
            FROM activity
            WHERE activity.daily_log_id = daily_log.id
        ) 
        AS has_activity,
        EXISTS (
            SELECT 1
            FROM health
            WHERE health.daily_log_id = daily_log.id
        )
        AS has_health
        FROM daily_log 
        WHERE daily_log.user_name=:user_name
        AND daily_log.date LIKE :year 
        ORDER BY daily_log.date
        """
    params = {
        "year": f"{year}-%", 
        "user_name": current_user.name
    }
    rows = execute_qry(qry, params)
    return [
        {
            "date": row[0], 
            "has_activity": bool(row[1]), 
            "has_health": bool(row[2])
        } 
        for row in rows
    ]  