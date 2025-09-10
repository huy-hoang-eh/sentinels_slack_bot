from slack_bolt import App

from src.application.services.get_jira_summary import get_jira_summary
from src.infrastructure.messaging.slack.notifier import post_message


def handle_summary(ack, respond, command):
  ack("Generating sprint summary...")

  summary = get_jira_summary(command.get("channel_id"), command.get("text"))
  post_message(command.get("channel_id"), str(summary))