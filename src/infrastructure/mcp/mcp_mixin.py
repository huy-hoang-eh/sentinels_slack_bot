from typing import Any
from fastmcp import Client

from src.config.mcp import Mcp

class McpMixin:
  _mcp_client: Client | None = None
  _history: list[Any] = []

  def is_session_opened(self):
    return self._mcp_client is not None and self._mcp_client.is_connected()

  async def open_session(self):
    config = Mcp.to_dict()

    self._mcp_client = Client(config)
    await self._mcp_client.__aenter__()
    self._history = []
    return self._mcp_client

  async def close_session(self):
    if self.is_session_opened():
      await self._mcp_client.__aexit__(None, None, None)
      self._mcp_client = None
      self._history = []