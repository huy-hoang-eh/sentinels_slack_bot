from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

_LOADED_NOTIFIER: bool = False
_SLACK_CLIENT: WebClient = None

def initialize(app: App):
  global _LOADED_NOTIFIER, _SLACK_CLIENT

  if _LOADED_NOTIFIER:
    return
  _LOADED_NOTIFIER = True
  _SLACK_CLIENT = app.client


def post_message(channel_id: str, text: str):
  try:
    _SLACK_CLIENT.chat_postMessage(channel=channel_id, text=text)
  except SlackApiError as e:
    print(f"Error posting message to Slack: {e.response['error']}")




