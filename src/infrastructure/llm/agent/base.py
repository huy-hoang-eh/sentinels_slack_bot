from abc import ABC, abstractmethod
from fastmcp import Client

from src.config.env import Env
from src.config.mcp import Mcp
from src.infrastructure.mcp.decorator import mcp_decorator

class Base(ABC):
  @mcp_decorator
  @abstractmethod
  async def prompt(self, session, prompt: str):
    pass  