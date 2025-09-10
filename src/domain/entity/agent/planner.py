import json
from google.genai import types
from src.config.agent import Agent
from src.infrastructure.llm.adapter import Adapter
from src.domain.entity.agent.common.plan import Plan
from src.domain.entity.agent.tools import Tools

class Planner:
  def __init__(self, template_path: str):
    self._template_path = template_path
    self._agent = Adapter(Agent.GEMINI)

  def _load_template(self) -> str:
    """Load the planning template and replace the user_goal placeholder."""
    try:
      with open(self._template_path, 'r', encoding='utf-8') as file:
        template = file.read()
      return template
    except FileNotFoundError:
      # Fallback to basic prompt if template not found
      return f"""
      You are an intelligent task planning agent that create a step-by-step plan to achieve the following goal. 
      User's Goal: **user_goal**
      Available tools: **available_tools**
      """

  async def call(self, prompt: str) -> Plan:
    tools = await Tools().call()

    await self._agent.open_session()

    template = self._load_template()

    response = await self._agent.send_message(
      template.replace("*user_goal*", prompt).replace("*available_tools*", json.dumps(tools)),
      {
        'temperature': 0,
        'response_mime_type': 'application/json',
        'response_schema': Plan
      }
    )
    await self._agent.close_session()
    return response.parsed
