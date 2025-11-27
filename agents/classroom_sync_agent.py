"""
Classroom Sync Agent - Google ADK version.
Fetches student assignments from Google Classroom using ADK Agent.
"""
from typing import Dict, Any, Optional
import os
import sys
import time

# Import observability
from core.observability import logger, tracer, metrics

# Import MCP
import asyncio
import os
import ast
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@tracer.trace_agent("classroom_sync")
def run_classroom_sync(student_id: str) -> Dict[str, Any]:
    """
    Fetch assignments for a student using MCP.
    
    Args:
        student_id: The student's ID
        
    Returns:
        Dictionary with assignments list
    """
    logger.log_agent_start("classroom_sync", student_id)
    
    with metrics.track_agent("classroom_sync"):
        start_time = time.time()
        
        async def fetch_assignments_mcp():
            # Create server parameters
            server_params = StdioServerParameters(
                command=sys.executable,
                args=["-m", "tools.google_classroom_server"],
                env=os.environ.copy()  # Pass environment variables
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize session
                    await session.initialize()
                    
                    # Trace and log tool call
                    tool_name = "list_assignments_for_student"
                    tool_args = {"student_id": student_id}
                    
                    logger.log_tool_call(tool_name, tool_args, "classroom_sync")
                    
                    with tracer.trace_span(f"tool.{tool_name}") as span:
                        start_ts = time.time()
                        try:
                            # Call the tool
                            result = await session.call_tool(tool_name, arguments=tool_args)
                            duration = (time.time() - start_ts) * 1000
                            
                            # Log success
                            logger.log_tool_result(tool_name, duration, True)
                            
                            # Parse result
                            if result.content and hasattr(result.content[0], "text"):
                                return ast.literal_eval(result.content[0].text)
                            return []
                        except Exception as e:
                            duration = (time.time() - start_ts) * 1000
                            logger.log_tool_result(tool_name, duration, False, str(e))
                            raise

        try:
            assignments = asyncio.run(fetch_assignments_mcp())
        except Exception as e:
            print(f"Error calling MCP tool: {e}")
            assignments = []

        duration_ms = (time.time() - start_time) * 1000
        
        result = {"assignments": assignments}
        logger.log_agent_complete("classroom_sync", duration_ms, result)
        return result



