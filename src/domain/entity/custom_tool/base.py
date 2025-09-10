from typing import Any
from mcp import types

class Base:
  @classmethod
  def inputSchema(cls) -> dict:
    pass

  @classmethod
  async def call(cls, arguments: dict[str, Any] | None = None) -> types.CallToolResult:
    pass
  
  @classmethod
  def name(cls) -> str:
    """
    Generate a dynamic name based on the full module path and class name.
    This allows for dynamic importing and unique identification of custom tools.
    """
    module_path = cls.__module__
    class_name = cls.__name__
    return f"{module_path}-{class_name}"
  
  @classmethod
  def description(cls) -> str:
    return "This is a custom tool"