from slack_bolt import App

from .sprint_summary import register_sprint_summary_command

def register_all_commands(app: App):
  register_sprint_summary_command(app)