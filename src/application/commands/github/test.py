from slack_bolt import App
from src.infrastructure.messaging.slack.notifier import post_message


def handle_test(ack, respond, command):
    """Handle the github test command."""
    ack("Processing github test command...")
    
    # Example github test functionality
    message = f"Github test command executed! Channel: {command.get('channel_id')}, Text: {command.get('text', 'No text provided')}"
    post_message(command.get("channel_id"), message)

