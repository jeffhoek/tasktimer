from pydantic import BaseModel


class NewTaskItem(BaseModel):
    description: str


class TaskItem(BaseModel):
    id: int
    user_id: str


class TaskOut(BaseModel):
    id: int
    description: str
    time_spent: float
