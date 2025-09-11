from typing import Any
from mcp import types
from .base import Base
import importlib

class Adapter:
  @classmethod
  def _get_custom_tool(cls, name: str) -> Base:
    try:
      module_name = "src.domain.entity." + name
      class_name = "".join(map(lambda x: x.capitalize(), name.split(".")[-1].split("_")))
      module = importlib.import_module(module_name)
      cls = getattr(module, class_name)
      return cls
    except Exception as e:
      raise Exception(f"Failed to get custom tool {name}: {e}")

  @classmethod
  async def call_tool(cls, name: str, arguments: dict[str, Any] | None = None) -> types.CallToolResult:
    tool = cls._get_custom_tool(name)
    return await tool.call(arguments)