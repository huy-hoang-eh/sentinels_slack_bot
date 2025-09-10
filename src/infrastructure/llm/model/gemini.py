import json
from typing import Optional
from google import genai
from google.genai import types

from src.config.env import Env
from .base import Base


class Gemini(Base):
  def __init__(self, model: str = "gemini-2.5-flash"):
    super().__init__()
    self._model = model
    self._client = genai.Client(api_key=Env["GEMINI_API_TOKEN"])
    self._conversation: Optional[types.ChatMessage] = None

  def _clean_schema(self, schema: dict) -> dict:
    """Clean MCP tool schema to be compatible with Gemini API"""
    if not isinstance(schema, dict):
      return schema
    
    # Fields to exclude from Gemini tool schemas
    excluded_fields = {
      "additionalProperties", 
      "$schema", 
      "additional_properties"
    }
     
    cleaned = {}
    for key, value in schema.items():
      if key in excluded_fields:
        continue

      if isinstance(value, dict):
        cleaned[key] = self._clean_schema(value)
      elif isinstance(value, list):
        cleaned[key] = [self._clean_schema(item) if isinstance(item, dict) else item for item in value]
      else:
        cleaned[key] = value

    return cleaned
      
  async def _get_converted_mcp_tools(self, config: dict | None = None) -> list[dict]:
    tools = await self.available_tools()

    return [
      {
        "name": tool.name,
        "description": tool.description,
        "parameters": self._clean_schema(tool.inputSchema)
      } for tool in tools
    ]

  async def _parse_config(self, config: dict | None) -> dict | None:
    if config is None:
      return None

    # Create a copy to avoid modifying the original
    gemini_config = config.copy()
    
    if "use_tools" in gemini_config:
      if gemini_config["use_tools"] == True:
        gemini_config["tools"] = [
          types.Tool(
            function_declarations=(
              await self._get_converted_mcp_tools(config) + await self._get_converted_custom_tools(config)
            )
          )
        ]
      del gemini_config["use_tools"]
    return types.GenerateContentConfig(**gemini_config)
  
  async def send_message(self, prompt: str, config: dict | None = None) -> types.GenerateContentResponse:
    if not self.is_session_opened():
      raise Exception("Conversation not opened")

    gemini_config = await self._parse_config(config)

    self._history.append(
      types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
      )
    )

    final_response = None
    response = None
    stop_reason = None
    has_function_calls = False

    while True:
      if stop_reason is not None and not has_function_calls:
        break

      response = self._client.models.generate_content(
        model=self._model,
        contents=self._history,
        config=gemini_config
      )

      final_response = response

      candidate = response.candidates[0]
      
      stop_reason = candidate.finish_reason

      result, has_function_calls = await self._handle_response(candidate)

      t_messages = []
      for item in result:
        t_messages.extend(item["messages"])

      self._history.extend(
        self._make_messages(
          self._merge_messages(t_messages)
        )
      )
    
    return final_response
  
  async def _handle_response(self, candidate: types.Candidate) -> list[dict]:
    if candidate.content is None:
      return []
    
    result = []
    has_function_calls = False
    
    for part in candidate.content.parts:
      if part.function_call is not None:
        has_function_calls = True
        result.append(await self._handle_tool_use(part))
      elif part.text is not None:
        result.append(self._handle_text(part))

    return result, has_function_calls

  async def _handle_tool_use(self, part: types.Part):
    tool_result = await self.call_tool(name=part.function_call.name, arguments=part.function_call.args)

    content = json.loads(tool_result.content[0].text)
  
    if type(content) == list:
      response = content[0]
    else:
      response = content

    return {
      "messages": [
        {
          "role": "model",
          "content": [part]
        },
        {
          "role": "user",
          "content": [
            types.Part(
              function_response=types.FunctionResponse(
                id=part.function_call.id,
                name=part.function_call.name,
                response=response
              )
            )
          ]
        }
      ],
      "responses": [f"Call {part.function_call.name} with args {part.function_call.args}: {response}"]
    }

  def _handle_text(self, part: types.Part):
    return {
      "messages": [
        {
          "role": "model",
          "content": [part]
        }
      ],
      "responses": [part.text]
    }
  
  def _make_messages(self, messages: list[dict]):
    return [
      types.Content(
        role=message["role"],
        parts=message["content"]
      ) for message in messages
    ]
