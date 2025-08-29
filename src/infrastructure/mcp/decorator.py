from fastmcp import Client

from src.config.env import Env
from src.config.mcp import Mcp

def mcp(func):
  async def wrapper(self, *args, **kwargs):
    config = Mcp.to_dict()
    for server_name in config["mcpServers"]:
      config["mcpServers"][server_name]["env"] = Env.to_dict()
    
    mcp_client = Client(config)
    async with mcp_client:
      response = await func(self, mcp_client.session, *args, **kwargs)
    return response
  return wrapper