from typing import Any

from fastmcp import Client
from mcp import types
from src.config.mcp import Mcp
from src.domain.entity.custom_tool.adapter import Adapter

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

  def _is_custom_tool(self, tool_name: str) -> bool:
    return tool_name.startswith("src.domain.entity.custom_tool.")

  async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> types.CallToolResult:
    if self._is_custom_tool(name):
      return await Adapter.call_tool(name=name, arguments=arguments)
    else:
      return await self._mcp_client.call_tool(name=name, arguments=arguments)