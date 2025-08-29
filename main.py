from dotenv import load_dotenv

from src.application.commands import register_all_commands
from src.config.env import Env
from src.infrastructure.messaging.slack.notifier import initialize as initialize_notifier

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

app = App(token=Env["SLACK_BOT_TOKEN"])

initialize_notifier(app)

register_all_commands(app)

if __name__ == "__main__":
    print("🤖 Slack bot is running...")
    handler = SocketModeHandler(app, Env["SLACK_APP_TOKEN"])
    handler.start()

