import os
import sys
import json
from pathlib import Path
from src.config.env import Env
from typing import Any, Dict


_CONFIG: Dict[str, Any] = {}
_LOADED: bool = False
ROOT_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH: str = os.path.join(ROOT_DIR, "config", "mcp.json")


def initialize() -> None:
  global _CONFIG, _LOADED, CONFIG_PATH
  if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError("MCP config not found at config/mcp.json")
  try:
    with open(CONFIG_PATH, "r") as f:
      data = json.load(f)
    if not isinstance(data.get("mcpServers"), dict):
      raise ValueError("missing 'mcpServers' object")
    
    for server_name in data["mcpServers"]:
      data["mcpServers"][server_name]["env"] = Env.to_dict()

      if data["mcpServers"][server_name]["command"] == "docker":
        volume_mount = f"{Env['LOCAL_CERTIFICATE_PATH']}:{Env['IMAGE_CERTIFICATE_PATH']}:ro"
        
        data["mcpServers"][server_name]["args"].insert(0, volume_mount)
        data["mcpServers"][server_name]["args"].insert(0, "-v")
        data["mcpServers"][server_name]["args"].insert(0, "--rm")
        data["mcpServers"][server_name]["args"].insert(0, "-i")
        data["mcpServers"][server_name]["args"].insert(0, "run")

    _CONFIG = data
    _LOADED = True
  except Exception as e:
    raise ValueError(f"Invalid MCP config: {e}")


class Mcp:
  @classmethod
  def __class_getitem__(cls, key: str) -> Dict[str, Any]:
    try:
      if not _LOADED:
        raise RuntimeError("MCP config not initialized. Call initialize() at startup.")
      servers = _CONFIG["mcpServers"]
      server_cfg = servers[key]
      return server_cfg
    except Exception as e:
      raise ValueError(f"Invalid MCP server config for '{key}': {e}")
  
  @classmethod
  def to_dict(cls) -> dict[str, Any]:
    try:
      if not _LOADED:
        raise RuntimeError("MCP config not initialized. Call initialize() at startup.")
      return _CONFIG
    except Exception as e:
      raise ValueError(f"Invalid MCP config: {e}")


def providers() -> list[str]:
  try:
    if not _LOADED:
      raise RuntimeError("MCP config not initialized. Call initialize() at startup.")
    return list((_CONFIG.get("mcpServers") or {}).keys())
  except Exception as e:
    raise ValueError(f"Unable to list MCP providers: {e}")

