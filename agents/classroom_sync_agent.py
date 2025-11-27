"""
Classroom Sync Agent - Google ADK version.
Fetches student assignments from Google Classroom using ADK Agent.
"""
from core.config import STUDENT_EMAILS
from typing import Dict, Any, Optional
import os
import sys
import time

# Import observability
from core.observability import logger, tracer, metrics

# Import MCP
try:
    import asyncio
    import os
    import ast
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    from tools.google_classroom_tool import list_assignments_for_student

@tracer.trace_agent("classroom_sync")
@tracer.trace_agent("classroom_sync")
def run_classroom_sync(student_id: str) -> Dict[str, Any]:
    """
    Fetch assignments from Google Classroom for all configured student accounts.
    
    Args:
        student_id: Primary student ID (used for logging context)
        
    Returns:
        Dictionary containing list of assignments
    """
    logger.log_agent_start("classroom_sync", {"student_id": student_id})
    
    all_assignments = []
    
    # Iterate over all configured student emails to fetch assignments
    for email in STUDENT_EMAILS:
        logger.info(f"Fetching assignments for {email}")
        
        if MCP_AVAILABLE:
            try:
                # TEMPORARY: Direct call is safer given we just updated the tool signature
                # and we know MCP is currently falling back anyway.
                assignments = list_assignments_for_student(email)
                all_assignments.extend(assignments)
                
            except Exception as e:
                logger.error(f"Error fetching assignments for {email}: {e}")
        else:
            # Fallback to direct call
            print(f"MCP not available, calling tool directly for {email}.")
            try:
                assignments = list_assignments_for_student(email)
                all_assignments.extend(assignments)
            except Exception as e:
                print(f"Error calling tool directly for {email}: {e}")

    logger.log_agent_complete(
        "classroom_sync", 
        {"assignments": [a['title'] for a in all_assignments]}
    )
    
    return {
        "assignments": all_assignments
    }

