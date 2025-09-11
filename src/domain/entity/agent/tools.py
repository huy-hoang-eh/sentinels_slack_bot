import json
from src.config.agent import Agent
from src.infrastructure.llm.adapter import Adapter
from typing import List, Dict
from src.config.template import Template
from src.domain.entity.custom_tool.jira.omit_issue_data_for_summary import OmitIssueDataForSummary

class Tools:
  def __init__(self):
      self._template_path = Template.TOOLS
      self._agent = Adapter(Agent.GEMINI)

  def _load_template(self) -> str:
    """Load the tools template."""
    try:
      with open(self._template_path, 'r', encoding='utf-8') as file:
        template = file.read()
      return template
    except FileNotFoundError:
      # Fallback to basic prompt if template not found
      return """
        You are a tool discovery agent. List all available tools in the system and return a JSON array with this format:
        [
            {
            "name": "tool_name",
            "description": "Brief description of what this tool does"
            }
        ]
            
        Analyze the available tools and provide comprehensive information about each one.
      """
  async def call(self) -> List[Dict[str, str]]:
    await self._agent.open_session()

    template = self._load_template()

    response = await self._agent.send_message(
      template,
      {
        'temperature': 0,
        'use_tools': True,
        'custom_tools': [
          OmitIssueDataForSummary
        ]
      }
    )

    await self._agent.close_session()

    # Parse JSON response
    try:
      raw_text = response.candidates[0].content.parts[0].text
      # Remove markdown code blocks if present
      if '```' in raw_text:
        raw_text = raw_text.split('```')[1].replace('json', '').strip()
      
      return json.loads(raw_text)
    except Exception:
      return []