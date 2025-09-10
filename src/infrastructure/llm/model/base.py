from abc import ABC, abstractmethod

from google.genai import types

from src.infrastructure.mcp.mcp_mixin import McpMixin


class Base(McpMixin):
  def __init__(self):
    super().__init__()
    self._mcp_client = None

  async def _get_converted_mcp_tools(self, config: dict | None = None) -> list[dict]:
    return [{
      "name": tool.name,
      "description": tool.description,
      "input_schema": tool.inputSchema,
    } for tool in await self.available_tools()]

  async def _get_converted_custom_tools(self, config: dict | None = None) -> list[dict]:
    if "custom_tools" not in config:
      return []
      
    tools = config["custom_tools"]

    return [
      {
        "name": tool.name(),
        "description": tool.description(),
        "parameters": tool.inputSchema()
      } for tool in tools
    ]
  
  @abstractmethod
  async def send_message(self, prompt: str, config: dict | None = None):
    pass

  async def available_tools(self) -> list[dict]:
    if not self.is_session_opened():
      return []
    
    tools = await self._mcp_client.list_tools()

    return tools

  def _parse_config(self, config: dict | None) -> dict | None:
    return config

  def _merge_messages(self, messages: list[dict]):
    merged_messages = {}
    for message in messages:
      key = message["role"]
      if key not in merged_messages:
        merged_messages[key] = []
      merged_messages[key].extend(message["content"])

    converted_messages = []
    for key in merged_messages:
      converted_messages.append({
        "role": key,
        "content": merged_messages[key]
      })

    return converted_messages  