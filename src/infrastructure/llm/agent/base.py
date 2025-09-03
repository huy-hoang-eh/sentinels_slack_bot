from abc import ABC, abstractmethod

from google.genai import types

from src.infrastructure.mcp.mcp_mixin import McpMixin


class Base(McpMixin):
  def __init__(self):
    super().__init__()
    self._mcp_client = None

  @abstractmethod
  async def send_message(self, prompt: str, config: dict | None = None) -> str:
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