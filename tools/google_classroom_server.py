"""
Google Classroom MCP Server.
Provides MCP-compatible tool interface for Google Classroom API.
"""
import asyncio
from typing import Any

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP not available")

from tools.google_classroom_tool import list_assignments_for_student as _list_assignments

# Create MCP server
if MCP_AVAILABLE:
    server = Server("google-classroom")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        return [
            Tool(
                name="list_assignments_for_student",
                description="Fetch all assignments for a student from Google Classroom",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "student_id": {
                            "type": "string",
                            "description": "The student's ID or email"
                        }
                    },
                    "required": ["student_id"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Execute tool."""
        if name == "list_assignments_for_student":
            # Call the actual function
            result = _list_assignments(arguments["student_id"])
            return [TextContent(
                type="text",
                text=str(result)
            )]
        raise ValueError(f"Unknown tool: {name}")


# Run server
async def main():
    """Run MCP server."""
    if not MCP_AVAILABLE:
        print("MCP not available. Exiting.")
        return
    
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
