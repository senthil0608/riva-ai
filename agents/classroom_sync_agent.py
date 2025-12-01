"""
Classroom Sync Agent - Google ADK version.
Fetches student assignments from Google Classroom using ADK Agent.
"""
import os
import sys
import time
from typing import Dict, Any, Optional
from core.db import get_active_student

# Import observability
from core.observability import logger, tracer, metrics

# Configuration
# We now fetch this dynamically from DB
# STUDENT_EMAILS = os.getenv("STUDENT_EMAILS", "").split(",")

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

# Always import the tool function as we use it directly now
from tools.google_classroom_tool import list_assignments_for_student

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
    
    # Fetch student emails from DB
    user = get_active_student(student_id)
    student_emails = user['student_emails'] if user else []

    # Iterate over all configured student emails to fetch assignments
    for email in student_emails:
        logger.info(f"Fetching assignments for: {email}")
        
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

