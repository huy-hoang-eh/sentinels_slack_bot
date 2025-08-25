from slack_bolt import App

from src.infrastructure.slack_notifier import SlackNotifier
from src.infrastructure.jira_client import JiraClient

from .sprint_summary import register_sprint_summary_command

def register_all_commands(app: App, notifier: SlackNotifier, jira_client: JiraClient):
  register_sprint_summary_command(app, notifier, jira_client)