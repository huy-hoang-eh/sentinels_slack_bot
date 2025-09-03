import asyncio

from src.config.agent import Agent
from src.config.env import Env

from src.infrastructure.llm.adapter import Adapter


DEFAULT_PROMPT = "Summary current sprint of board name: sentinels board"

def get_jira_summary(channel_id: str | None, prompt: str | None = None) -> str:
  if channel_id is None:
    raise Exception("Channel_id can not be null")
  
  if not prompt:
    prompt = DEFAULT_PROMPT
  
  return asyncio.run(
    _ask_agent(
      Agent.GEMINI, 
      prompt.strip(),
    )
  )


async def _ask_agent(agent: str, prompt: str):
  adapter = Adapter(agent)
  await adapter.open_session()
  response = await adapter.send_message(
    prompt,
    {
      "temperature": 0,
      "system_instruction": _make_system_instruction(),
    }
  )

  await adapter.close_session()


  return response

def _make_system_instruction() -> str:
  return f"""
You are an automated JIRA reporting agent.
You receive user's prompt and you need to provide a well-formatted summary.
Jira base URL: {Env["JIRA_URL"]}

## MCP TOOL FIELD SELECTION GUIDELINES
When using MCP tools with input_schema fields, apply these optimization strategies:

### REQUIRED FIELD SELECTION PRINCIPLES:
1. **Response-Driven Selection**: Only request fields that directly contribute to the final response format, avoiding use of `*all` or `*`
2. **Use JQL to search fields**: When searching fields, use JQL to search fields
3. **Minimal Data Fetching**: Choose the smallest set of fields that satisfy the output requirements
4. **Performance Optimization**: Avoid fetching large text fields (descriptions, comments) unless specifically needed
5. **Exclude Unused Fields**: Never include metadata fields, url fields, internal IDs, or metadata that doesn't contribute to the summary

### FIELDS TO ALWAYS EXCLUDE:
- **URL Fields**: `*_url`, `icon_url`, `avatar_url`, `self`, `url` (these are for UI rendering, not reporting), `html`
- **Internal Metadata**: `id`, `expand`, `requested_fields`, `custom_fields` (unless specifically analyzing custom fields)
- **Large Text Fields**: `description`, `comments`, `attachments`, `changelogs` (unless content analysis is required)
- **Nested Objects**: Avoid deep object expansion unless the specific nested data is needed

### FIELD SELECTION BY USE CASE:
- **For Epic Summaries**: Use fields: `summary,status,assignee,priority,issuetype,updated,labels,parent`
- **For Status Counts**: Use fields: `status,issuetype,parent` (minimal set for grouping and counting)
- **For Issue Lists**: Use fields: `summary,status,assignee,priority,issuetype,created,updated`
- **For Detailed Analysis**: Add fields: `description,labels,fixVersions,components` only when needed
- **For Sprint Reports**: Use fields: `summary,status,assignee,issuetype,parent,updated,priority`

Your response must be a list of json objects with the following format:
- epic: The name of epic
- overall_status: The overall status of the epic (must be the number of issues in each status)
"""

def _make_test_jira_info_prompt(prompt: str) -> str:
  jira_base = (Env["JIRA_URL"] or "").strip()
  return f"""
You are a Jira assistant with MCP tools access. 
Interpret the user's prompt and provide a well-formatted summary.
## CONTEXT
- Jira base URL: {jira_base}

## USER'S PROMPT
{prompt}

## OUTPUT FORMAT
- Just return the summary
"""

def _make_jira_info_prompt(prompt: str) -> str:
  jira_base = (Env["JIRA_URL"] or "").strip()
  return f"""
You are a Jira assistant with MCP tools access. 
Interpret the user's prompt and provide a well-formatted summary.

## STRICT RULES
- Always use MCP tools for real data.
- Handle errors gracefully with suggestions.
- If board search fails, apply these fallback strategies:
  * Strip plural forms and common suffixes
  * Remove generic terms like "board", "project", "team"
  * Extract and search using only the core business name
  * Use fuzzy matching on the simplified search term

## CONTEXT
- Jira base URL: {jira_base}

## USER'S PROMPT
{prompt}

## APPROACH
- Board/Sprint: Use MCP to get boards → sprints → issues. Group by Epic with status breakdown.
- Board Search Strategy: 
  1. Try exact board name first
  2. If no results, apply these transformations sequentially:
     - Remove plural suffixes from the search term
     - Remove common words like "board", "boards", "project"
     - Extract the core keyword and search with that
  3. Use progressive simplification until a match is found
  4. Prioritize partial matching over exact matching for board discovery
- Projects: Get project issues, provide health summary.
- Search: Use JQL with fields: summary,status,assignee,priority,issuetype,updated,labels
- Specific Issues: Get detailed issue info.

## OUTPUT FORMAT:
Sprint/Board Summaries:
- Epic groupings with empty lines between
- Status counts: "*Overall Status:* X 📝 To Do, Y ⏳ In Progress, Z 🔎 Review, W ✅ Done"
- Bullet lists with stickers: 📝 To Do, ⏳ In Progress, 🔎 Review, ✅ Done

## General: Use markdown tables, show metrics, highlight blockers/overdue items.
## Issue Details: Show key, title, status, assignee, priority, dates, Epic relationships.

## STRUCTURE: Brief overview → Main content → Key insights → Action items (if applicable)

## BOARD NAME RESOLUTION PROCESS:
- Start with the user's exact input as the initial search term
- If no matches found, progressively simplify the search term by removing:
  * Plural endings (s, es, ies)
  * Generic descriptors (board, project, team, space)
  * Extra whitespace and special characters
- Continue simplifying until a board is found or all options exhausted
- Always prioritize fuzzy matching over exact string matching for better user experience

"""