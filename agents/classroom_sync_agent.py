"""
Classroom Sync Agent - Google ADK version.
Fetches student assignments from Google Classroom using ADK Agent.
"""
import os
import sys
import time
from typing import List
from core.models import Assignment, AssignmentState
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
def run_classroom_sync(student_id: str) -> List[Assignment]:
    """
    Fetch assignments from Google Classroom for all configured student accounts.
    
    Args:
        student_id: Primary student ID (used for logging context)
        
    Returns:
        List of Assignment objects
    """
    logger.log_agent_start("classroom_sync", {"student_id": student_id})
    
    all_assignments: List[Assignment] = []
    
    # Fetch student emails from DB
    user = get_active_student()
    student_emails = user['student_emails'] if user else []

    # Iterate over all configured student emails to fetch assignments
    for email in student_emails:
        logger.info(f"Fetching assignments for: {email}")
        
        raw_assignments = []
        if MCP_AVAILABLE:
            try:
                # TEMPORARY: Direct call is safer given we just updated the tool signature
                # and we know MCP is currently falling back anyway.
                raw_assignments = list_assignments_for_student(email)
            except Exception as e:
                logger.error(f"Error fetching assignments for {email}: {e}")
        else:
            # Fallback to direct call
            print(f"MCP not available, calling tool directly for {email}.")
            try:
                raw_assignments = list_assignments_for_student(email)
            except Exception as e:
                print(f"Error calling tool directly for {email}: {e}")
        
        # Convert raw dicts to Pydantic models
        for raw in raw_assignments:
            try:
                # Map 'state' string to Enum if needed, or let Pydantic handle it
                # Ensure 'due' is handled correctly if it's "No due date"
                due_date = raw.get('due')
                if due_date == "No due date":
                    due_date = None
                
                assignment = Assignment(
                    id=raw.get('id'),
                    title=raw.get('title'),
                    subject=raw.get('subject'),
                    due=due_date,
                    state=raw.get('state', 'UNKNOWN'),
                    description=raw.get('description', ''),
                    course_id=raw.get('course_id')
                )
                all_assignments.append(assignment)
            except Exception as e:
                logger.error(f"Error parsing assignment {raw.get('id')}: {e}")

    logger.log_agent_complete(
        "classroom_sync", 
        {"assignments": [a.title for a in all_assignments]}
    )
    
    return all_assignments

