from google import genai
from google.genai import types

from src.infrastructure.mcp.decorator import mcp_decorator
from src.config.env import Env
from .base import Base


class Gemini(Base):
  def __init__(self, model: str = "gemini-2.5-flash"):
    super().__init__()
    self._model = model
    self._client = genai.Client(api_key=Env["GEMINI_API_TOKEN"])
  
  @mcp_decorator
  async def prompt(self, session, prompt: str):
    chat = self._client.aio.chats.create(
      model=self._model,
      config=types.GenerateContentConfig(
        temperature=0,
        tools=[session],
      )
    )

    response = await chat.send_message(
      message=prompt
    )

    return response
  
  # def generate_sprint_summary(self, sprint_name: str, issues: list[dict]) -> str:
    issues_str = f"# Sprint Name: {sprint_name}"

    for issue in issues:
      parent = getattr(issue.fields, 'parent', None)
    
      if parent:  
        issue_str = f"""
        # Parent summary: {parent.fields.summary}
        # Parent type: {parent.fields.issuetype}
        # Issue type: {issue.fields.issuetype}
        # Issue Summary: {issue.fields.summary}
        # Issue Status: {issue.fields.status}
        \n
        """

        issues_str += issue_str


    prompt = f"""
    **## ROLE:**
    You are an automated JIRA reporting agent. Your only function is to parse raw JIRA issue data and convert it into a clean, structured, and consistent Markdown summary.

    **## TASK:**
    Generate a project status report by summarizing the provided list of JIRA issues.

    **## STRICT RULES:**
    1.  The output MUST be valid Markdown.
    2.  Group issues by parent Epic. Omit the group if it would be empty.
    3.  Start each Epic group with exactly: `*Epic: {{Parent Summary}}*`.
    4.  Immediately after that line, add one line beginning with `*Overall Status:*` followed by comma-separated counts for present statuses among To Do, In Progress, Review, Done.
        - Omit any status whose count is 0.
        - Order the statuses as: To Do, In Progress, Review, Done.
        - Exclude Won't Do entirely (do not count or display it).
    5.  After the overall status line, add one bullet per present status in this exact format:
        `- *[{{Issue Status}}]:* {{Summary content}}`.
        - {{Summary content}} MUST be a synthesized summary (not a list of all items). It should:
          - Aggregate themes across the status using {{ Issue Type }} and {{ Issue Summary }}.
          - Mention notable deliverables, risks/blockers, and quantify counts by type where useful (e.g., "7 Sub-tasks, 1 Bug").
          - Use neutral, concise language in present tense. Max 5 sentences.
        - Allowed values for `{{Issue Status}}`: To Do, In Progress, Review, Done.
        - Order the bullets as: To Do, In Progress, Review, Done.
        - Do not include a bullet for Won't Do.
    6.  Normalize common status synonyms:
        - Backlog, Open, Todo -> To Do
        - Doing, In-Flight, WIP -> In Progress
        - Code Review, In Review, PR Review, QA Review -> Review
        - Won't Fix, Won't Do, Canceled -> exclude entirely
    7.  Formatting constraints:
        - Use hyphen bullets (`- `) with exactly one space after the hyphen.
        - Use a single space after commas in the overall status line.
        - Do not add any headings, bolding, or text other than specified.
        - Insert exactly one blank line between two Epic groups.
        - Prefix each status with these stickers in both the overall status line and the per-status bullets:
          - To Do -> 📝
          - In Progress -> ⏳
          - Review -> 🔎
          - Done -> ✅
    8.  Do NOT include any text after the final bullet.

    **# EXAMPLE:**

      **## Input Data Example:**
      Sprint Name: {{Sprint Name}}
    
      # Parent summary: User Authentication Flow
      # Parent type: Epic
      # Issue type: Task
      # Issue Summary: Design the login page UI
      # Issue Status: In Progress

      # Parent summary: User Authentication Flow
      # Parent type: Epic
      # Issue type: Sub-task
      # Issue Summary: Implement email/password login logic
      # Issue Status: In Progress

      # Parent summary: User Authentication Flow
      # Parent type: Epic
      # Issue type: Bug
      # Issue Summary: API crashes when user record is not found
      # Issue Status: To Do

      # Parent summary: User Authentication Flow
      # Parent type: Epic
      # Issue type: Task
      # Issue Summary: Peer review login form validation
      # Issue Status: Review

      # Parent summary: User Authentication Flow
      # Parent type: Epic
      # Issue type: Task
      # Issue Summary: Add unit tests for auth service
      # Issue Status: Done

      # Parent summary: User Flow
      # Parent type: Epic
      # Issue type: Task
      # Issue Summary: Test the login page UI
      # Issue Status: Done

      **## End of Input Data Example**

      **## Output Data:**

        **### Predefined formats:**

        [Per Epic]
        - *Overall Status:* X 📝 To Do, Y ⏳ In Progress, Z 🔎 Review, W ✅ Done
          - *[📝 To Do]:* {{Summary content}}
          - *[⏳ In Progress]:* {{Summary content}}
          - *[🔎 Review]:* {{Summary content}}
          - *[✅ Done]:* {{Summary content}}

        **### End of Predefined formats**

        **### Required Output Format for each Epic:**

        [{{Sprint Name}} Summary]
        *Epic: {{Parent Summary}}*
        - *Overall Status:* X 📝 To Do, Y ⏳ In Progress, Z 🔎 Review, W ✅ Done
          - *[{{Issue Status}}]:* {{Summary content}}

        **### End of Required Output Format for each Epic**

        **### Output Data Example:**

        [{{Sprint Name}} Summary]
        *Epic: User Authentication Flow*
        - *Overall Status:* 1 📝 To Do, 2 ⏳ In Progress, 1 🔎 Review, 1 ✅ Done
          - *[📝 To Do]:* Triage login API edge case for missing users.
          - *[⏳ In Progress]:* Building login UI and auth flow; integrating email/password.
          - *[🔎 Review]:* Validating form rules and UX for login. 
          - *[✅ Done]:* Added unit tests for auth service.

        *Epic: User Flow*
        - *Overall Status:* 1 ✅ Done
          - *[✅ Done]:* Executed login UI test scenario.

        **### End of Output Data Example:**

      **## End of Output Data**

    **## End of Example**
    ---
    **## JIRA DATA FOR CURRENT REPORT:**

    {issues_str}

    **### End of JIRA DATA FOR CURRENT REPORT**
    """
    return self.generate_text(prompt)


