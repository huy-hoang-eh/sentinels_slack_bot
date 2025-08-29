import os
from typing import Any, Dict, List, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.types import Tool
from mcp.client.stdio import stdio_client

from src.config.env import Env
from src.config.mcp import Mcp

class McpServer:
  def __init__(self):
    self._config = Mcp.to_dict()
    for server_name in self._config["mcpServers"]:
      self._config["mcpServers"][server_name]["env"] = Env.to_dict()

  
class Base:
  """Base MCP stdio client that loads server definition from JSON config.

  Subclasses must define `server_name`. If missing, an exception is raised.
  Config path is `config/mcp.json`.
  """

  server_name: Optional[str] = None

  def __init__(self) -> None:
    if not self.server_name:
      raise ValueError("server_name must be defined in subclass")

    command: str
    args: List[str]

    server_cfg = Mcp[self.server_name]
    command = server_cfg["command"]
    args = server_cfg["args"]

    self._params = StdioServerParameters(command=command, args=args, env=Env.to_dict())
    # Persistent resources owned by a dedicated asyncio loop thread
    self._exit_stack: Optional[AsyncExitStack] = None
    self._session: Optional[ClientSession] = None
    self._list_tools: Optional[list[Tool]] = None
    self._loop = asyncio.new_event_loop()
    self._loop_ready = Event()
    self._thread = Thread(target=self._run_loop, name=f"MCP-{self.server_name}-Loop", daemon=True)
    self._thread.start()
    self._loop_ready.wait(timeout=5)
    # Initialize session inside the loop
    init_future = asyncio.run_coroutine_threadsafe(self._async_init(), self._loop)
    init_future.result()

  def _run_loop(self):
    asyncio.set_event_loop(self._loop)
    self._loop_ready.set()
    self._loop.run_forever()

  async def _async_init(self):
    self._exit_stack = AsyncExitStack()
    stdio_transport = await self._exit_stack.enter_async_context(
      stdio_client(self._params)
    )
    self._stdio, self._write = stdio_transport
    self._session = await self._exit_stack.enter_async_context(
      ClientSession(self._stdio, self._write)
    )
    await self._session.initialize()

  async def _ensure_session(self) -> ClientSession:
    if self._session is None:
      await self._async_init()
    return self._session  # type: ignore[return-value]

  async def list_tools(self) -> list[Tool]:
    if self._list_tools is None:
      session = await self._ensure_session()
      list_tools = await session.list_tools()
      self._list_tools = list_tools.tools
    return self._list_tools

  def list_tools_sync(self) -> list[Tool]:
    future = asyncio.run_coroutine_threadsafe(self.list_tools(), self._loop)
    return future.result()

  async def call_tool(self, name: str, arguments: Dict[str, Any]):
    session = await self._ensure_session()
    return await session.call_tool(name, arguments)

  def call_tool_sync(self, name: str, arguments: Dict[str, Any]):
    future = asyncio.run_coroutine_threadsafe(self.call_tool(name, arguments), self._loop)
    return future.result()

  async def clean_up(self) -> None:
    if self._exit_stack is not None:
      await self._exit_stack.aclose()
    self._session = None

  def shutdown(self) -> None:
    # Ensure session closed then stop loop and join thread
    close_future = asyncio.run_coroutine_threadsafe(self.clean_up(), self._loop)
    close_future.result()
    self._loop.call_soon_threadsafe(self._loop.stop)
    self._thread.join(timeout=2)


