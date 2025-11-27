"""
Calendar Mapper MCP Server.
Provides MCP-compatible tool interface for calendar time slots.
"""
import asyncio
from typing import Any

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from tools.calendar_mapper_tool import get_available_time_slots as _get_slots

if MCP_AVAILABLE:
    server = Server("calendar-mapper")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="get_available_time_slots",
                description="Get available time slots for a student",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "The student's ID"
                        }
                    },
                    "required": ["student_id"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name == "get_available_time_slots":
            result = _get_slots(arguments["student_id"])
            return [TextContent(type="text", text=str(result))]
        raise ValueError(f"Unknown tool: {name}")


async def main():
    if not MCP_AVAILABLE:
        return
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
