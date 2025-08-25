from slack_bolt import App

from src.config.jira_board import JiraBoard
from src.infrastructure.slack_notifier import SlackNotifier

def register_sprint_summary_command(app: App, notifier: SlackNotifier):
  @app.command("/sprint-summary")
  def handle_sprint_summary_command(ack, respond, command):
    ack("On it! Fetching the lastest sprint data and generating the summary...")
    try:
        board_name = command.get("text")
        board_id = JiraBoard[board_name.lower()]
        respond(f"🤖 Fetching the lastest sprint data and generating the summary for {board_name} - {board_id}")

        channel_id = command.get("channel_id")
        if channel_id:
          notifier.post_message(channel_id, f"Sprint summary generation started for {board_name} (board {board_id})")
    except Exception as e:
        print(f"Error fetching sprint data: {e}")