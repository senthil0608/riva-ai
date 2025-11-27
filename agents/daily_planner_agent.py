"""
Daily Planner Agent - Google ADK version.
Creates personalized daily schedules using Gemini LLM.
"""
from typing import Dict, Any, List
import os
import sys

# Import MCP
import asyncio
import os
import ast
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import observability
from core.observability import logger, tracer




def run_daily_planner(
    student_id: str,
    assignments: List[Dict[str, Any]],
    skill_profile: Dict[str, str]
) -> Dict[str, Any]:
    """
    Create a daily plan for the student.
    Fallback function when ADK not available.
    
    Args:
        student_id: The student's ID
        assignments: List of assignments
        skill_profile: Student's skill levels by subject
        
    Returns:
        Dictionary with daily plan
    """
    slots = []
    
    async def fetch_slots_mcp():
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "tools.calendar_mapper_server"],
            env=os.environ.copy()
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tool_name = "get_available_time_slots"
                tool_args = {"student_id": student_id}
                
                logger.log_tool_call(tool_name, tool_args, "daily_planner")
                
                with tracer.trace_span(f"tool.{tool_name}") as span:
                    start_ts = time.time()
                    try:
                        result = await session.call_tool(
                            tool_name,
                            arguments=tool_args
                        )
                        duration = (time.time() - start_ts) * 1000
                        logger.log_tool_result(tool_name, duration, True)
                        
                        if result.content and hasattr(result.content[0], "text"):
                            return ast.literal_eval(result.content[0].text)
                        return []
                    except Exception as e:
                        duration = (time.time() - start_ts) * 1000
                        logger.log_tool_result(tool_name, duration, False, str(e))
                        raise
    
    try:
        slots = asyncio.run(fetch_slots_mcp())
    except Exception as e:
        print(f"Error calling MCP tool: {e}")
        slots = []
            
    daily_plan = []
    for i, assignment in enumerate(assignments[:len(slots)]):
        difficulty_tag = skill_profile.get(assignment.get("subject", ""), "on_track")
        daily_plan.append({
            "time": slots[i],
            "task_id": assignment["id"],
            "title": assignment["title"],
            "subject": assignment["subject"],
            "difficulty_tag": difficulty_tag
        })
    
    return {"daily_plan": daily_plan}



