from fastmcp import Client

from src.config.env import Env
from src.config.mcp import Mcp

class McpMixin:
  def is_session_opened(self):
    return self._mcp_client is not None and self._mcp_client.is_connected()

  async def open_session(self):
    config = Mcp.to_dict()
    for server_name in config["mcpServers"]:
      config["mcpServers"][server_name]["env"] = Env.to_dict()
    
    self._mcp_client = Client(config)
    await self._mcp_client.__aenter__()
    return self._mcp_client

  async def close_session(self):
    if self.is_session_opened():
      await self._mcp_client.__aexit__(None, None, None)
      self._mcp_client = None