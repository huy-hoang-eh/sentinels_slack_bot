import json
from typing import Optional
from google import genai
from google.genai import types

from src.config.env import Env
from .base import Base


class Gemini(Base):
  def __init__(self, model: str = "gemini-2.5-flash"):
    super().__init__()
    self._model = model
    self._client = genai.Client(api_key=Env["GEMINI_API_TOKEN"])
    self._conversation: Optional[types.ChatMessage] = None
  
  def _clean_schema(self, schema: dict) -> dict:
    """Clean MCP tool schema to be compatible with Gemini API"""
    if not isinstance(schema, dict):
      return schema
    
    # Fields to exclude from Gemini tool schemas
    excluded_fields = {
      "additionalProperties", 
      "$schema", 
      "additional_properties"
    }
    
    cleaned = {}
    for key, value in schema.items():
      if key in excluded_fields:
        continue
        
      if isinstance(value, dict):
        cleaned[key] = self._clean_schema(value)
      elif isinstance(value, list):
        cleaned[key] = [self._clean_schema(item) if isinstance(item, dict) else item for item in value]
      else:
        cleaned[key] = value
    
    return cleaned

  async def _parse_config(self, config: dict | None) -> dict | None:
    if config is None:
      return None

    # Create a copy to avoid modifying the original
    gemini_config = config.copy()

    tools = await self.available_tools()
    if tools:
      gemini_config["tools"] = [
        types.Tool(
          function_declarations=[
            {
              "name": tool.name,
              "description": tool.description,
              "parameters": self._clean_schema(tool.inputSchema)
            } for tool in tools
          ]
        )
      ]
    
    # gemini_config["automatic_function_calling"] = types.AutomaticFunctionCallingConfig(
    #   disable=True
    # )
    
    return types.GenerateContentConfig(**gemini_config)
  
  async def send_message(self, prompt: str, config: dict | None = None) -> str:
    if not self.is_session_opened():
      raise Exception("Conversation not opened")

    config = await self._parse_config(config)

    self._history.append(
      types.Content(
        role="user",
        parts=[types.Part(text=prompt)]
      )
    )

    final_response = []
    response = None
    stop_reason = None
    has_function_calls = False

    while True:
      if stop_reason is not None and not has_function_calls:
        break

      response = self._client.models.generate_content(
        model=self._model,
        contents=self._history,
        config=config
      )

      candidate = response.candidates[0]
      
      stop_reason = candidate.finish_reason

      result, has_function_calls = await self._handle_response(candidate)

      t_messages = []
      for item in result:
        t_messages.extend(item["messages"])
        final_response.extend(item["responses"])

      self._history.extend(
        self._make_messages(
          self._merge_messages(t_messages)
        )
      )
    
    return "test"
  
  async def _handle_response(self, candidate: types.Candidate) -> list[dict]:
    if candidate.content is None:
      return []
    
    result = []
    has_function_calls = False
    
    for part in candidate.content.parts:
      if part.function_call is not None:
        has_function_calls = True
        result.append(await self._handle_tool_use(part))
      elif part.text is not None:
        result.append(self._handle_text(part))

    return result, has_function_calls

  async def _handle_tool_use(self, part: types.Part):
    tool_result = await self._mcp_client.call_tool(name=part.function_call.name, arguments=part.function_call.args)

    content = json.loads(tool_result.content[0].text)
  
    if type(content) == list:
      response = content[0]
    else:
      response = content

    return {
      "messages": [
        {
          "role": "model",
          "content": [part]
        },
        {
          "role": "user",
          "content": [
            types.Part(
              function_response=types.FunctionResponse(
                id=part.function_call.id,
                name=part.function_call.name,
                response=response
              )
            )
          ]
        }
      ],
      "responses": [f"Call {part.function_call.name} with args {part.function_call.args}: {response}"]
    }

  def _handle_text(self, part: types.Part):
    return {
      "messages": [
        {
          "role": "model",
          "content": [part]
        }
      ],
      "responses": [part.text]
    }
  
  def _make_messages(self, messages: list[dict]):
    return [
      types.Content(
        role=message["role"],
        parts=message["content"]
      ) for message in messages
    ]

  # def generate_sprint_summary(self, sprint_name: str, issues: list[dict]) -> str:
  #   issues_str = f"# Sprint Name: {sprint_name}"

  #   for issue in issues:
  #     parent = getattr(issue.fields, 'parent', None)
    
  #     if parent:  
  #       issue_str = f"""
  #       # Parent summary: {parent.fields.summary}
  #       # Parent type: {parent.fields.issuetype}
  #       # Issue type: {issue.fields.issuetype}
  #       # Issue Summary: {issue.fields.summary}
  #       # Issue Status: {issue.fields.status}
  #       \n
  #       """

  #       issues_str += issue_str


  #   prompt = f"""
  #   **## ROLE:**
  #   You are an automated JIRA reporting agent. Your only function is to parse raw JIRA issue data and convert it into a clean, structured, and consistent Markdown summary.

  #   **## TASK:**
  #   Generate a project status report by summarizing the provided list of JIRA issues.

  #   **## STRICT RULES:**
  #   1.  The output MUST be valid Markdown.
  #   2.  Group issues by parent Epic. Omit the group if it would be empty.
  #   3.  Start each Epic group with exactly: `*Epic: {{Parent Summary}}*`.
  #   4.  Immediately after that line, add one line beginning with `*Overall Status:*` followed by comma-separated counts for present statuses among To Do, In Progress, Review, Done.
  #       - Omit any status whose count is 0.
  #       - Order the statuses as: To Do, In Progress, Review, Done.
  #       - Exclude Won't Do entirely (do not count or display it).
  #   5.  After the overall status line, add one bullet per present status in this exact format:
  #       `- *[{{Issue Status}}]:* {{Summary content}}`.
  #       - {{Summary content}} MUST be a synthesized summary (not a list of all items). It should:
  #         - Aggregate themes across the status using {{ Issue Type }} and {{ Issue Summary }}.
  #         - Mention notable deliverables, risks/blockers, and quantify counts by type where useful (e.g., "7 Sub-tasks, 1 Bug").
  #         - Use neutral, concise language in present tense. Max 5 sentences.
  #       - Allowed values for `{{Issue Status}}`: To Do, In Progress, Review, Done.
  #       - Order the bullets as: To Do, In Progress, Review, Done.
  #       - Do not include a bullet for Won't Do.
  #   6.  Normalize common status synonyms:
  #       - Backlog, Open, Todo -> To Do
  #       - Doing, In-Flight, WIP -> In Progress
  #       - Code Review, In Review, PR Review, QA Review -> Review
  #       - Won't Fix, Won't Do, Canceled -> exclude entirely
  #   7.  Formatting constraints:
  #       - Use hyphen bullets (`- `) with exactly one space after the hyphen.
  #       - Use a single space after commas in the overall status line.
  #       - Do not add any headings, bolding, or text other than specified.
  #       - Insert exactly one blank line between two Epic groups.
  #       - Prefix each status with these stickers in both the overall status line and the per-status bullets:
  #         - To Do -> 📝
  #         - In Progress -> ⏳
  #         - Review -> 🔎
  #         - Done -> ✅
  #   8.  Do NOT include any text after the final bullet.

  #   **# EXAMPLE:**

  #     **## Input Data Example:**
  #     Sprint Name: {{Sprint Name}}
    
  #     # Parent summary: User Authentication Flow
  #     # Parent type: Epic
  #     # Issue type: Task
  #     # Issue Summary: Design the login page UI
  #     # Issue Status: In Progress

  #     # Parent summary: User Authentication Flow
  #     # Parent type: Epic
  #     # Issue type: Sub-task
  #     # Issue Summary: Implement email/password login logic
  #     # Issue Status: In Progress

  #     # Parent summary: User Authentication Flow
  #     # Parent type: Epic
  #     # Issue type: Bug
  #     # Issue Summary: API crashes when user record is not found
  #     # Issue Status: To Do

  #     # Parent summary: User Authentication Flow
  #     # Parent type: Epic
  #     # Issue type: Task
  #     # Issue Summary: Peer review login form validation
  #     # Issue Status: Review

  #     # Parent summary: User Authentication Flow
  #     # Parent type: Epic
  #     # Issue type: Task
  #     # Issue Summary: Add unit tests for auth service
  #     # Issue Status: Done

  #     # Parent summary: User Flow
  #     # Parent type: Epic
  #     # Issue type: Task
  #     # Issue Summary: Test the login page UI
  #     # Issue Status: Done

  #     **## End of Input Data Example**

  #     **## Output Data:**

  #       **### Predefined formats:**

  #       [Per Epic]
  #       - *Overall Status:* X 📝 To Do, Y ⏳ In Progress, Z 🔎 Review, W ✅ Done
  #         - *[📝 To Do]:* {{Summary content}}
  #         - *[⏳ In Progress]:* {{Summary content}}
  #         - *[🔎 Review]:* {{Summary content}}
  #         - *[✅ Done]:* {{Summary content}}

  #       **### End of Predefined formats**

  #       **### Required Output Format for each Epic:**

  #       [{{Sprint Name}} Summary]
  #       *Epic: {{Parent Summary}}*
  #       - *Overall Status:* X 📝 To Do, Y ⏳ In Progress, Z 🔎 Review, W ✅ Done
  #         - *[{{Issue Status}}]:* {{Summary content}}

  #       **### End of Required Output Format for each Epic**

  #       **### Output Data Example:**

  #       [{{Sprint Name}} Summary]
  #       *Epic: User Authentication Flow*
  #       - *Overall Status:* 1 📝 To Do, 2 ⏳ In Progress, 1 🔎 Review, 1 ✅ Done
  #         - *[📝 To Do]:* Triage login API edge case for missing users.
  #         - *[⏳ In Progress]:* Building login UI and auth flow; integrating email/password.
  #         - *[🔎 Review]:* Validating form rules and UX for login. 
  #         - *[✅ Done]:* Added unit tests for auth service.

  #       *Epic: User Flow*
  #       - *Overall Status:* 1 ✅ Done
  #         - *[✅ Done]:* Executed login UI test scenario.

  #       **### End of Output Data Example:**

  #     **## End of Output Data**

  #   **## End of Example**
  #   ---
  #   **## JIRA DATA FOR CURRENT REPORT:**

  #   {issues_str}

  #   **### End of JIRA DATA FOR CURRENT REPORT**
  #   """
  #   return self.generate_text(prompt)


