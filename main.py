from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

import uvicorn

from web import calendar, activity, running, walking, cycling, weightlifting, health, user, pages
 
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(health.router)
app.include_router(activity.router)
app.include_router(running.router) 
app.include_router(walking.router)
app.include_router(cycling.router)
app.include_router(weightlifting.router)
app.include_router(calendar.router)
app.include_router(user.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True) 