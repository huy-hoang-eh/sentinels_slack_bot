import asyncio

from src.config.agent import Agent
from src.config.env import Env

from src.infrastructure.llm.adapter import Adapter


DEFAULT_PROMPT = "Summary current sprint of board name: sentinels boards"

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
  session =await adapter.open_session()
  response = await adapter.send_message(
    _make_jira_info_prompt(prompt),
    {
      "temperature": 0,
      "session": session,
    }
  )

  await adapter.close_session()

  

  return response

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