from fastmcp import Client

from src.config.env import Env
from src.config.mcp import Mcp

async def open_session():
  """Alternative 1: Manual session management - returns client and session"""
  config = Mcp.to_dict()
  for server_name in config["mcpServers"]:
    config["mcpServers"][server_name]["env"] = Env.to_dict()
  
  mcp_client = Client(config)
  await mcp_client.__aenter__()
  return mcp_client

async def close_session(mcp_client):
  """Close the manually opened session"""
  await mcp_client.__aexit__(None, None, None)
