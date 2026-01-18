from contextlib import asynccontextmanager
from datetime import time, datetime
from database import database, task_table
from fastapi import FastAPI, HTTPException
from models import (
    TaskOut,
    NewTaskItem, TaskItem)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


@app.post("/track", response_model=TaskItem)
async def track(task: NewTaskItem):
    print(task)
    data = {**task.model_dump(), "start_time": datetime.now()}
    query = task_table.insert().values(data)
    last_record_id = await database.execute(query)

    return {"id": last_record_id, "user_id": task.user_id}


@app.post("/stop", response_model=TaskItem)
async def stop(task: TaskItem):
    select_query = task_table.select().where(
        (task_table.c.id == task.id) & (task_table.c.user_id == task.user_id)
    )
    existing_task = await database.fetch_one(select_query)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    end_time = datetime.now()
    update_query = (
        task_table.update().where(task_table.c.id == task.id).where(task_table.c.user_id == task.user_id).values(end_time=end_time)
    )
    await database.execute(update_query)
    return task


@app.get("/times", response_model=list[TaskOut])
async def get_times(user_id: int, date: str):
    # Using `int` and `str` parameters instead of Pydantic models
    # tells FastAPI we want to get these values from the query string.
    selected_date = datetime.strptime(date, "%Y-%m-%d").date()
    start_of_day = datetime.combine(selected_date, time.min)
    end_of_day = datetime.combine(selected_date, time.max)

    query = task_table.select().where(
        (task_table.c.user_id == user_id)
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
