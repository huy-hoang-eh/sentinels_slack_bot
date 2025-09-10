from pydantic import BaseModel
from src.domain.entity.agent.common.task import Task

class Plan(BaseModel):
  goal: str
  steps: list[Task]