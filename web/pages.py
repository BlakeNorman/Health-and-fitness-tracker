from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from service import user as user_service

from datetime import date

router = APIRouter()

# Calendar
@router.get("/calendar") 
def home():
    return FileResponse("templates/calendar.html") 

# Login
@router.get("/")
def login():
    return FileResponse("templates/user/login.html")

# Create Account
@router.get("/register")
def register():
    return FileResponse("templates/user/register.html")

# Change Password or Delete Account
@router.get("/account")
def account():
    return FileResponse("templates/user/account.html")

# Request Password Reset
@router.get("/request-password-reset")
def request_password_reset():
    return FileResponse("templates/user/request_password_reset.html")

# Reset Password
@router.get("/reset-password/{token}")
def reset_password(token):
    try:
        user_service.validate_reset_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return FileResponse("templates/user/reset_password.html")

# Daily log of specified date
@router.get("/calendar/{activity_date}")
def calendar_day(activity_date: date): 
    return FileResponse("templates/daily_log.html")

# Create activity on specified date   
@router.get("/create-activity/{activity_date}")
def create_activity(activity_date: date):
    return FileResponse("templates/create_activity.html")

# Create running activity log on specified date   
@router.get("/create-activity/running/{activity_date}")
def create_run(activity_date: date):
    return FileResponse("templates/running/create_run.html")

# Edit running activity log on specified date   
@router.get("/edit-activity/running/{activity_id}")
def modify_run(activity_id: int):
    return FileResponse("templates/running/modify_run.html")

# Create walking activity log on specified date   
@router.get("/create-activity/walking/{activity_date}")
def create_walk(activity_date: date):
    return FileResponse("templates/walking/create_walk.html")

# Edit walking activity log on specified date   
@router.get("/edit-activity/walking/{activity_id}")
def modify_walk(activity_id: int):
    return FileResponse("templates/walking/modify_walk.html")

# Create cycling activity log on specified date   
@router.get("/create-activity/cycling/{activity_date}")
def create_cycle(activity_date: date):
    return FileResponse("templates/cycling/create_cycle.html")

# Edit cycling activity log on specified date   
@router.get("/edit-activity/cycling/{activity_id}")
def modify_cycle(activity_id: int):
    return FileResponse("templates/cycling/modify_cycle.html")

# Create weightlifting activity log on specified date   
@router.get("/create-activity/weightlifting/{activity_date}")
def create_weightlifting_session(activity_date: date):
    return FileResponse("templates/weightlifting/create_weightlifting_session.html")

# Edit weightlifting activity log on specified date   
@router.get("/edit-activity/weightlifting/{activity_id}")
def modify_weightlifting_session(activity_id: int):
    return FileResponse("templates/weightlifting/modify_weightlifting_session.html")

# Create health log on specified date   
@router.get("/create-health-log/{activity_date}")
def create_health_log(activity_date: date):
    return FileResponse("templates/health/create_health_log.html")

# Edit health log log with specified id   
@router.get("/edit-health-log/{id}")
def modify_health_log(id: int):
    return FileResponse("templates/health/modify_health_log.html") 

# Graphs 
@router.get("/data-visualizations")
def data_visualization():
    return FileResponse("templates/data_visualizations.html") 