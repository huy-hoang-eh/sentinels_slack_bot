from abc import ABC, abstractmethod
from mcp.types import Tool
from src.infrastructure.mcp.server.atlassian import Atlassian
from src.infrastructure.mcp.server.base import Base

class Adapter(ABC):
  def __init__(self):
    self._mcps = {
      "atlassian": Atlassian(),
    }

  def get_mcp(self, server: str) -> Base:
    return self._mcps[server]

  def get_tools(self, server: str | None = None) -> list[Tool]:
    if server is None:
      tools: list[Tool] = []
      for mcp in self._mcps.values():
        tools.extend(mcp.list_tools_sync())
      return tools
    
    return self._mcps[server].list_tools_sync()

  def clean_up(self):
    for mcp in self._mcps.values():
      mcp.shutdown()