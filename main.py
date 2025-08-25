from dotenv import load_dotenv

from src.application.commands import register_all_commands
from src.config.env import Env

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

app = App(token=Env["SLACK_BOT_TOKEN"])

register_all_commands(app)

if __name__ == "__main__":
    print("🤖 Slack bot is running...")
    handler = SocketModeHandler(app, Env["SLACK_APP_TOKEN"])
    handler.start()

