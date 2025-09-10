from slack_bolt import App
from src.infrastructure.messaging.slack.notifier import post_message


def handle_test(ack, respond, command):
    """Handle the test command."""
    ack("Processing test command...")
    
    # Example test functionality
    message = f"Test command executed! Channel: {command.get('channel_id')}, Text: {command.get('text', 'No text provided')}"
    post_message(command.get("channel_id"), message)

