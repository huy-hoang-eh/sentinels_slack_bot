from pydantic import BaseModel
from .task import Task

class Plan(BaseModel):
  goal: str
  steps: list[Task]