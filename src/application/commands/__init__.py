from slack_bolt import App

from src.infrastructure.slack_notifier import SlackNotifier

from .sprint_summary import register_sprint_summary_command

def register_all_commands(app: App, notifier: SlackNotifier):
  register_sprint_summary_command(app, notifier)