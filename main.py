from dotenv import load_dotenv
load_dotenv()

from src.application.commands import register_all_commands
from src.config.env import Env
from src.infrastructure.messaging.slack.notifier import initialize as initialize_notifier

from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import ssl

custom_ca_path = Env["CA_CERTIFICATE_PATH"]
ssl_context = ssl.create_default_context(cafile=custom_ca_path)
client = WebClient(token=Env["SLACK_BOT_TOKEN"], ssl=ssl_context)

app = App(token=Env["SLACK_BOT_TOKEN"], client=client)
initialize_notifier(app)

register_all_commands(app)

if __name__ == "__main__":
    print("🤖 Slack bot is running...")
    handler = SocketModeHandler(app, Env["SLACK_APP_TOKEN"])
    handler.start()

