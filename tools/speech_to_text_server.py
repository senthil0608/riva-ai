"""
Speech-to-Text MCP Server.
Provides MCP-compatible tool interface for speech-to-text.
"""
import asyncio
from typing import Any

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

from tools.speech_to_text_tool import transcribe_audio as _transcribe

if MCP_AVAILABLE:
    server = Server("speech-to-text")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="transcribe_audio",
                description="Transcribe audio to text using speech-to-text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "audio_data": {
                            "type": "string",
                            "description": "Base64 encoded audio data"
                        }
                    },
                    "required": ["audio_data"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        if name == "transcribe_audio":
            result = _transcribe(arguments["audio_data"])
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
