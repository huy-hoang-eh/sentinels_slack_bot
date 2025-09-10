from slack_bolt import App
import importlib
import pkgutil
from src.infrastructure.messaging.slack.notifier import post_message


def _decorate_handler(handler_fn):
  def wrapper(ack, respond, command):
    ack()
    try:
      handler_fn(ack, respond, command)
    except Exception as e:
      # respond expects a message text, not channel. Use post_message for channel targeting
      post_message(command.get("channel_id"), f"Error handling command: {e}")  
  return wrapper

def _register_commands_recursive(app: App, package_name: str, package_path: list, prefix: str = ""):
  """Recursively register commands from packages and subpackages."""
  for _, name, ispkg in pkgutil.iter_modules(package_path):
    if name.startswith("_"):
      continue
    
    full_module_name = f"{package_name}.{name}"
    
    if ispkg:
      # Handle subpackage - recursively register commands with folder prefix
      subpackage = importlib.import_module(full_module_name)
      folder_prefix = f"{prefix}{name}-" if prefix else f"{name}-"
      _register_commands_recursive(app, full_module_name, subpackage.__path__, folder_prefix)
    else:
      # Handle module - try to register command
      try:
        module = importlib.import_module(full_module_name)
        handler_name = f"handle_{name}"
        handler_fn = getattr(module, handler_name, None)
        
        if callable(handler_fn):
          # Create command name with folder prefix
          command_name = f"{prefix}{name}".replace('_', '-')
          slash_command = f"/{command_name}"
          app.command(slash_command)(_decorate_handler(handler_fn))
          print(f"Registered command: {slash_command}")
      except ImportError as e:
        print(f"Failed to import module {full_module_name}: {e}")

def register_all_commands(app: App):
  """Register all commands from the commands package and its subpackages."""
  package = __name__
  _register_commands_recursive(app, package, __path__)