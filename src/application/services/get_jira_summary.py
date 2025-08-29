import asyncio

from src.config.agent import Agent
from src.config.env import Env

from src.infrastructure.llm.adapter import prompt


DEFAULT_BOARD_INFO = "board sentinels"

def get_jira_summary(channel_id: str | None, board_info: str = DEFAULT_BOARD_INFO) -> str:
  if channel_id is None:
    raise Exception("Channel_id can not be null")
  
  if not board_info:
    board_info = DEFAULT_BOARD_INFO
  
  return asyncio.run(prompt(Agent.GEMINI, _make_board_info_prompt(board_info)))

# def _make_board_info_prompt(board_input: str) -> str:
#   jira_base = (Env["JIRA_URL"] or "").strip()
#   return f"""
#   Find the Jira board matching the user's input.

#   Context:
#   - Jira base URL: {jira_base}
#   - User input: "{board_input}"

#   Requirements:
#   - Interpret the input as a board name, key, or URL. Normalize whitespace/case.
#   - Prefer exact name match; if multiple, choose the highest-confidence single match.
#   - If ambiguous or no clear match, treat as no result.
#   - Hints for detection: JQL terms (project =, issuetype, sprint, board), Jira URL domains (e.g., atlassian.net), words like "board", "sprint".

#   Output target:
#   - A single, best-match board.
#   - If no suitable board: indicate none.
#   """

def _make_board_info_prompt(board_input: str) -> str:
  jira_base = (Env["JIRA_URL"] or "").strip()
  return f"""
  Find the Jira board matching the user's input.

  Context:
  - Jira base URL: {jira_base}
  - User input: "{board_input}"
  """