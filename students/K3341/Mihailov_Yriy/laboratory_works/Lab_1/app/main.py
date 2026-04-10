from fastapi import FastAPI

from app.api.assignments import router as assignments_router
from app.api.auth import router as auth_router
from app.api.tags import router as tags_router
from app.api.task_tags import router as task_tags_router
from app.api.tasks import router as tasks_router
from app.api.users import router as users_router

app = FastAPI(title="Time Manager")

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(tags_router)
app.include_router(assignments_router)
app.include_router(task_tags_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}

