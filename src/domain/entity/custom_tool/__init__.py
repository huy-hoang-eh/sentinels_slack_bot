"""
Custom tools module for MCP integration.
Provides base classes and utilities for dynamic tool loading and management.
"""

import importlib
import pkgutil
from typing import Dict, List, Type
from .base import Base


def discover_tools(package_path: str = "src.infrastructure.mcp.custom_tool") -> Dict[str, Type[Base]]:
    """
    Dynamically discover and import all custom tools in the package.
    
    Args:
        package_path: The package path to search for tools
        
    Returns:
        Dictionary mapping tool names to their classes
    """
    tools = {}
    
    # Get the current package
    try:
        package = importlib.import_module(package_path)
        package_dir = package.__path__
    except (ImportError, AttributeError):
        return tools
    
    # Walk through all modules in the package
    for _, module_name, is_pkg in pkgutil.walk_packages(package_dir, f"{package_path}."):
        if not is_pkg:  # Only process modules, not packages
            try:
                module = importlib.import_module(module_name)
                
                # Find all classes that inherit from Base
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and 
                        issubclass(attr, Base) and 
                        attr is not Base):
                        
                        tool_name = attr.name()
                        tools[tool_name] = attr
                        
            except ImportError as e:
                print(f"Warning: Could not import {module_name}: {e}")
                continue
    
    return tools


def get_tool_by_name(name: str) -> Type[Base]:
    """
    Dynamically load a tool by its name.
    
    Args:
        name: The tool name (e.g., "jira.omit_issue_data.OmitIssueData")
        
    Returns:
        The tool class
        
    Raises:
        ValueError: If the tool is not found
    """
    tools = discover_tools()
    
    if name not in tools:
        available_tools = list(tools.keys())
        raise ValueError(f"Tool '{name}' not found. Available tools: {available_tools}")
    
    return tools[name]


def import_class_from_strings(module_name: str, class_name: str) -> Type[Base]:
    """
    Import a tool class dynamically using module name and class name strings.
    
    Args:
        module_name: The full module path as string
        class_name: The class name as string
    
    Returns:
        The imported class
        
    Raises:
        ImportError: If the module cannot be imported
        AttributeError: If the class doesn't exist in the module
        TypeError: If the class doesn't inherit from Base
    """
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        # Get the class from the module
        cls = getattr(module, class_name)
        
        # Verify it's a subclass of Base
        if not (isinstance(cls, type) and issubclass(cls, Base)):
            raise TypeError(f"Class '{class_name}' is not a subclass of Base")
        
        return cls
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}': {e}")
    except AttributeError as e:
        raise AttributeError(f"Class '{class_name}' not found in module '{module_name}': {e}")


def import_class_from_full_path(full_path: str) -> Type[Base]:
    """
    Import a tool class from a full path string like "module.path.ClassName".
    This works with the output from the name() method.
    
    Args:
        full_path: Full path including module and class
    
    Returns:
        The imported class
    """
    # Split the path to separate module and class
    path_parts = full_path.split('.')
    class_name = path_parts[-1]
    module_name = '.'.join(path_parts[:-1])
    
    return import_class_from_strings(module_name, class_name)


def list_available_tools() -> List[str]:
    """
    Get a list of all available tool names.
    
    Returns:
        List of tool names
    """
    tools = discover_tools()
    return list(tools.keys())


__all__ = [
    "Base", 
    "discover_tools", 
    "get_tool_by_name", 
    "list_available_tools",
    "import_class_from_strings",
    "import_class_from_full_path"
]
