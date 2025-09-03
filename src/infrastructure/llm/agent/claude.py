import asyncio
from anthropic import Anthropic
from anthropic.types import ToolResultBlockParam, ToolUseBlock, TextBlock, Message
from src.config.env import Env
from .base import Base

class Claude(Base):
  STOP_REASON = ['end_turn', 'stop_sequence', 'max_tokens']
  def __init__(self, model: str = "claude-3-5-haiku-20241022"):
    super().__init__()
    self._model = model
    self._client = Anthropic(api_key=Env["ANTHROPIC_API_KEY"])

  async def _parse_config(self, config: dict | None) -> dict | None:
    if config is None:
      return None
    
    if "system_instruction" in config:
      config["system"] = [
        {
          "type": "text",
          "text": config["system_instruction"],
        }
      ]
      del config["system_instruction"]
    
    config["tools"] = [{
      "name": tool.name,
      "description": tool.description,
      "input_schema": tool.inputSchema,
    } for tool in await self.available_tools()]

    return config

  async def send_message(self, prompt: str, config: dict | None = None) -> str:
    if not self.is_session_opened():
      raise Exception("Conversation not opened")

    config = await self._parse_config(config)
    
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
