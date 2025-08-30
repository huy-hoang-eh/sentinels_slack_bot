from src.infrastructure.llm.agent.base import Base
from src.infrastructure.llm.agent.gemini import Gemini

class Adapter:
  _agent: Base | None = None
  
  def __init__(self, agent: str):
    self._agent = self._get_agent(agent)

  def _get_agent(self, agent: str) -> Base:
    if self._agent is not None:
      return self._agent
    
    if agent == "gemini":
      return Gemini() 
    else:
      raise ValueError(f"Agent {agent} not supported")

  async def open_session(self, config: dict = {}):
    return await self._agent.open_session(config)

  async def close_session(self):
    return await self._agent.close_session()

  async def send_message(self, message: str, config: dict | None = None):
    return await self._agent.send_message(message, config)