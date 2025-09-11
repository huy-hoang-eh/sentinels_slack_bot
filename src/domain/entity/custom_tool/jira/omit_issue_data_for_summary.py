from typing import Any
from mcp import types
from ..base import Base


class OmitIssueDataForSummary(Base):
    """
    Custom tool for omitting sensitive issue data from Jira responses for summary.
    """

    @classmethod
    def inputSchema(cls) -> dict:
        return {
            "type": "object",
            "properties": {
                "issues": {
                    "type": "object",
                    "description": "The Jira issue data to process for summary"
                },
            },
            "required": ["issues"]
        }
    
    @classmethod
    async def call(cls, arguments: dict[str, Any] | None = None) -> types.CallToolResult:
        return types.CallToolResult(
            content=[{}],
            is_error=False
        )
    
    @classmethod
    def description(cls) -> str:
        return "Omits fields from Jira issue data for summary"
