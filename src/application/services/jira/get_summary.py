import asyncio

from src.config.agent import Agent
from src.config.env import Env

from src.domain.use_case import jira


DEFAULT_PROMPT = "Summary current sprint of board name: sentinels board"

def get_summary(channel_id: str | None, prompt: str | None = None) -> str:
  if channel_id is None:
    raise Exception("Channel_id can not be null")
  
  if not prompt:
    prompt = DEFAULT_PROMPT
  
  return jira.get_summary(prompt)
