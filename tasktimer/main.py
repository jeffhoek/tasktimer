import os
from contextlib import asynccontextmanager
from datetime import time, datetime
from .database import database, task_table
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from .models import TaskOut, NewTaskItem, TaskItem
from .auth import get_current_user, AuthenticatedUser


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    """Health check endpoint for load balancer."""
    return {"status": "healthy"}


@app.post("/track", response_model=TaskItem)
async def track(
    task: NewTaskItem,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    data = {
        "description": task.description,
        "user_id": current_user.user_id,
        "start_time": datetime.now(),
    }
    query = task_table.insert().values(data)
    last_record_id = await database.execute(query)

    return {"id": last_record_id, "user_id": current_user.user_id}


@app.post("/stop", response_model=TaskItem)
async def stop(
    task_id: int,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    select_query = task_table.select().where(
        (task_table.c.id == task_id) & (task_table.c.user_id == current_user.user_id)
    )
    existing_task = await database.fetch_one(select_query)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    end_time = datetime.now()
    update_query = (
        task_table.update()
        .where(task_table.c.id == task_id)
        .where(task_table.c.user_id == current_user.user_id)
        .values(end_time=end_time)
    )
    await database.execute(update_query)
    return {"id": task_id, "user_id": current_user.user_id}


@app.get("/times", response_model=list[TaskOut])
async def get_times(
    date: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    start_of_day = datetime.combine(selected_date, time.min)
    end_of_day = datetime.combine(selected_date, time.max)

    query = task_table.select().where(
        (task_table.c.user_id == current_user.user_id)
        & (task_table.c.start_time <= end_of_day)
        & ((task_table.c.end_time >= start_of_day) | (task_table.c.end_time.is_(None)))
    )
    tasks = await database.fetch_all(query)

    result = []
    for task in tasks:
        end_time = task["end_time"]
        if task["end_time"] is None:
            end_time = datetime.now()

        actual_start = max(task["start_time"], start_of_day)
        actual_end = min(end_time, end_of_day)
        duration = actual_end - actual_start

        result.append({**task, "time_spent": duration.total_seconds()})

    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.getenv("PORT", 8080))
