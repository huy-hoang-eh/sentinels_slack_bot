import os

class Template:
  JIRA_PLAN: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/template/jira/plan.md"
  TOOLS: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/template/tools.md"