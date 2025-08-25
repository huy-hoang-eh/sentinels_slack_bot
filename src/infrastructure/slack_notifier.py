from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackNotifier:
  def __init__(self, client: WebClient):
    self._client = client

  def post_message(self, channel_id: str, text: str):
    try:
      self._client.chat_postMessage(channel=channel_id, text=text)
    except SlackApiError as e:
      print(f"Error posting message to Slack: {e.response['error']}")
