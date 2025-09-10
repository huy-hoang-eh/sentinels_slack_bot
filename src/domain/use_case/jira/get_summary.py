import asyncio

from src.domain.entity.agent.planner import Planner
from src.config.template import Template

def get_summary(prompt: str) -> str:
  planner = Planner(template_path=Template.JIRA_PLAN)

  plan = asyncio.run(planner.call(prompt))
  
  response = ""
  for step in plan.steps:
    str_step = f"Step {step.id}: {step.description}"
    print(str_step)
    response += str_step + "\n"

  return response