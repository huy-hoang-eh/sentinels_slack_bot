from slack_bolt import App

from src.config.env import Env
from src.config.jira_board import JiraBoard
from src.infrastructure.gemini_client import GeminiClient
from src.infrastructure.slack_notifier import SlackNotifier
from src.infrastructure.jira_client import JiraClient

def register_sprint_summary_command(app: App, notifier: SlackNotifier, jira_client: JiraClient):
  gemini_client = GeminiClient(Env["GEMINI_API_TOKEN"])

  @app.command("/sprint-summary")
  def handle_sprint_summary_command(ack, respond, command):
    ack("Generating sprint summary...")
    try:
        channel_id = command.get("channel_id")
        if channel_id:
          board_name = command.get("text")
          board_id = JiraBoard[board_name.lower()]
          
          if board_id:
            sprint = jira_client.current_sprint(board_id)
            issues = jira_client.issues_for_current_sprint(board_id)

            print(f"Sprint: {sprint.name}")

            summary = gemini_client.generate_sprint_summary(sprint.name, issues)

            notifier.post_message(channel_id, summary)
          else:
            notifier.post_message(channel_id, f"*Invalid board name*: {board_name}")

    except Exception as e:
        print(f"Error fetching sprint data: {e}")