from jira import JIRA

from src.config.env import Env

class JiraClient:
  def __init__(self, server: str, auth_context: tuple[str, str]):
    self._client = JIRA(
      server=server,
      basic_auth=auth_context
    )
  
  def active_sprints(self, board_id: str):
    return self._client.sprints(board_id, state="active")
  
  def current_sprint(self, board_id: str):
    sprints = self.active_sprints(board_id)
    if not sprints:
      raise ValueError(f"No active sprint found for board {board_id}")
    return sprints[0]

  def issues_for_sprint(self, sprint_id: int, jql_extra: str | None = None):
    jql = f"sprint = {sprint_id}"
    if jql_extra:
      jql = f"{jql} AND {jql_extra}"
    # maxResults=False will paginate through all results
    return list(self._client.search_issues(jql, fields="*all", maxResults=False))

  def issues_for_current_sprint(self, board_id: str, jql_extra: str | None = None):
    sprint = self.current_sprint(board_id)
    return self.issues_for_sprint(sprint.id, jql_extra=jql_extra)