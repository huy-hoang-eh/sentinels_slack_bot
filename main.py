from dotenv import load_dotenv

from src.application.commands import register_all_commands
from src.config.env import Env
from src.infrastructure.jira_client import JiraClient
from src.infrastructure.slack_notifier import SlackNotifier

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()

app = App(token=Env["SLACK_BOT_TOKEN"])
notifier = SlackNotifier(app.client)
jira_client = JiraClient(Env["JIRA_SERVER"], (Env["JIRA_USERNAME"], Env["JIRA_API_TOKEN"]))

register_all_commands(app, notifier, jira_client)

if __name__ == "__main__":
    print("🤖 Slack bot is running...")
    handler = SocketModeHandler(app, Env["SLACK_APP_TOKEN"])
    handler.start()

