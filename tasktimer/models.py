from pydantic import BaseModel


class NewTaskItem(BaseModel):
    user_id: int
    description: str


class TaskItem(BaseModel):
    id: int
    user_id: int


class TaskOut(BaseModel):
    id: int
    description: str
    time_spent: float
