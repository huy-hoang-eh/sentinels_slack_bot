from slack_bolt import App
import importlib
import pkgutil
from src.infrastructure.messaging.slack.notifier import post_message


def _decorate_handler(handler_fn):
  def wrapper(ack, respond, command):
    ack()
    handler_fn(ack, respond, command)
    try:
      handler_fn(ack, respond, command)
    except Exception as e:
      # respond expects a message text, not channel. Use post_message for channel targeting
      post_message(command.get("channel_id"), f"Error handling command: {e}")  
  return wrapper

def register_all_commands(app: App):
  package = __name__
  for _, name, ispkg in pkgutil.iter_modules(__path__):
    if ispkg or name.startswith("_"):
      continue
    module = importlib.import_module(f"{package}.{name}")

    handler_name = f"handle_{name}"
    handler_fn = getattr(module, handler_name, None)
    if callable(handler_fn):
      slash = f"/{name.replace('_', '-')}"
      app.command(slash)(_decorate_handler(handler_fn))