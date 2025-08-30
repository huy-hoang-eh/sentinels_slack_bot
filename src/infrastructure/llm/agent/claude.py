from anthropic import Anthropic
from src.infrastructure.mcp.adapter import open_session, close_session
from src.config.env import Env
from .base import Base

class Claude(Base):
  def __init__(self, model: str = "claude-3-5-haiku-20241022"):
    super().__init__()
    self._model = model
    self._client = Anthropic(api_key=Env["ANTHROPIC_API_KEY"])
    self._mcp_client = None

  def is_session_opened(self):
    return self._mcp_client is not None and self._mcp_client.is_connected()

  async def open_session(self, config: dict):
    if self.is_session_opened():
      return self._mcp_client.session
    
    self._mcp_client = await open_session()

    return self._mcp_client

  async def send_message(self, prompt: str, config: dict | None = None):
    if not self.is_session_opened():
      raise Exception("Conversation not opened")
    
    messages = [
      {
        "role": "user",
        "content": prompt
      }
    ]

    if config is not None:
      if "session" in config:
        session = config["session"]
        del config["session"]
        
        tools = await session.list_tools()
        available_tools = [{
          "name": tool.name,
          "description": tool.description,
          "input_schema": tool.inputSchema,
        } for tool in tools]

        config["tools"] = available_tools

    final_response = []
    assistant_message_content = []

    response = await self._client.messages.create(
      model=self._model,
      messages=messages,
      max_tokens=1000,
      **config
    )

    for content in response.content:
      if content.type == 'text':
        final_response.append(content.text)
        assistant_message_content.append(content.text)
      elif content.type == 'tool_use':
        tool_name = content.name
        tool_args = content.input

        result = await self._mcp_client.call_tool(tool_name, tool_args)

        assistant_message_content.append(content)
        final_response.append(f"Call tool {tool_name} with args {tool_args}")

        messages.append({
          "role": "assistant",
          "content": assistant_message_content
        })

        messages.append({
          "role": "user",
          "content": [
            {
              "type": "tool_result",
              "tool_use_id": content.id,
              "content": result.content
            }
          ]
          })
        
        response = await self._client.messages.create(
          model=self._model,
          messages=messages,
          max_tokens=1000,
          **config
        )
        
        final_response.append(response.content[0].text)

    return "\n".join(final_response)    
  
  async def close_session(self):
    if self.is_session_opened():
      await close_session(self._mcp_client)
      self._mcp_client = None