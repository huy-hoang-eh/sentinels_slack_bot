from slack_bolt import App

from src.config.jira_board import JiraBoard
from src.infrastructure.slack_notifier import SlackNotifier
from src.infrastructure.jira_client import JiraClient

def register_sprint_summary_command(app: App, notifier: SlackNotifier, jira_client: JiraClient):
  @app.command("/sprint-summary")
  def handle_sprint_summary_command(ack, respond, command):
    ack("Generating sprint summary...")
    try:
        channel_id = command.get("channel_id")
        if channel_id:
          board_name = command.get("text")
          board_id = JiraBoard[board_name.lower()]
          notifier.post_message(channel_id, f"Sprint summary generation started for {board_name} (board {board_id})")
          
          sprint = jira_client.current_sprint(board_id)
          issues = jira_client.issues_for_current_sprint(board_id)
          print(f"Current sprint: {sprint}")
          for issue in issues:
            print(f"Issue: #{issue.fields.parent}")
    except Exception as e:
        print(f"Error fetching sprint data: {e}")