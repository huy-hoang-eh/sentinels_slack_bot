import asyncio

from src.infrastructure.llm.agent.base import Base
from src.infrastructure.llm.agent.gemini import Gemini

def _get_agent(model: str) -> Base:
  if model == "gemini":
    return Gemini()
  else:
    raise ValueError(f"Model {model} not supported")

def prompt(model: str, message: str):
  agent = _get_agent(model)
  return agent.prompt(message)