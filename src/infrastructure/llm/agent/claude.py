import asyncio
from anthropic import Anthropic
from anthropic.types import ToolResultBlockParam, ToolUseBlock, TextBlock, Message
from src.infrastructure.mcp.adapter import open_session, close_session
from src.config.env import Env
from .base import Base

class Claude(Base):
  STOP_REASON = ['end_turn', 'stop_sequence', 'max_tokens']
  def __init__(self, model: str = "claude-3-5-haiku-20241022"):
    super().__init__()
    self._model = model
    self._client = Anthropic(api_key=Env["ANTHROPIC_API_KEY"])
    self._mcp_client = None

  async def _build_available_tools(self, session):
    tools = await session.list_tools()
    available_tools = [{
      "name": tool.name,
      "description": tool.description,
      "input_schema": tool.inputSchema,
    } for tool in tools]

    return available_tools

  def is_session_opened(self):
    return self._mcp_client is not None and self._mcp_client.is_connected()

  async def open_session(self, config: dict):
    if self.is_session_opened():
      return self._mcp_client
    
    self._mcp_client = await open_session()

    return self._mcp_client

  async def send_message(self, prompt: str, config: dict | None = None) -> str:
    if not self.is_session_opened():
      raise Exception("Conversation not opened")

    if config is not None and "session" in config:
      session = config["session"]
      del config["session"]
    
      config["tools"] = await self._build_available_tools(session)
    
    if config is not None and "system_instruction" in config:
      config["system"] = [
        {
          "type": "text",
          "text": config["system_instruction"],
        }
      ]
      del config["system_instruction"]
    
    messages = [
      {
        "role": "user",
        "content": [TextBlock(text=prompt, type="text")]
      }
    ]

    final_responses = []
    response = None
    stop_reason = None

    while True:
      if stop_reason in Claude.STOP_REASON:
        break

      response = self._client.messages.create(
        model=self._model,
        messages=messages,
        max_tokens=1000,
        **config
      )

      stop_reason = response.stop_reason

      result = await self._handle_response(response)

      t_messages = []
      for item in result:
        t_messages.extend(item["messages"])
        final_responses.extend(item["responses"])
      
      messages.extend(self._merge_messages(t_messages))

    return "\n".join(final_responses)    
  
  async def close_session(self):
    if self.is_session_opened():
      await close_session(self._mcp_client)
      self._mcp_client = None

  async def _handle_response(self, response: Message | None):
    if response is None or response.content is None:
      return []
    
    result = []

    for content in response.content:
      if content.type == 'tool_use':
        result.append(await self._handle_tool_use(content))
      elif content.type == 'text':
        result.append(self._handle_text(content))


    return result

  async def _handle_tool_use(self, content: ToolUseBlock):
    tool_result = await self._mcp_client.call_tool(name=content.name, arguments=content.input)
  
    return {
        "messages": [
          {
            "role": "assistant",
            "content": [content]
          },
          {
            "role": "user",
            "content": [
              ToolResultBlockParam(
                type="tool_result",
                tool_use_id=content.id,
                content=tool_result.content,
                is_error=tool_result.is_error
              )
            ]
          }
        ],
        "responses": [f"Call {content.name} with args {content.input}: {tool_result.content}"]
      }

  def _handle_text(self, content: TextBlock):
    return {
        "messages": [
          {
            "role": "assistant",
            "content": [content]
          }
        ],
        "responses": [content.text]
      }
  
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
