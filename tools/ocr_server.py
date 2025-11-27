"""
OCR MCP Server.
Provides MCP-compatible tool interface for OCR.
"""
import asyncio
from typing import Any

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from tools.ocr_tool import extract_text_from_image as _extract_text

if MCP_AVAILABLE:
    server = Server("ocr")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="extract_text_from_image",
                description="Extract text from an image using OCR",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_data": {
                            "type": "string",
                            "description": "Base64 encoded image data"
                        }
                    },
                    "required": ["image_data"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name == "extract_text_from_image":
            result = _extract_text(arguments["image_data"])
            return [TextContent(type="text", text=result)]
        raise ValueError(f"Unknown tool: {name}")


async def main():
    if not MCP_AVAILABLE:
        return
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
