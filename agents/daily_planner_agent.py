"""
Daily Planner Agent - Google ADK version.
Creates personalized daily schedules using Gemini LLM.
"""
from typing import Dict, Any, List
import os
import sys
import json
import re

# Import MCP
try:
    import asyncio
    import os
    import ast
    import time
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    from tools.calendar_mapper_tool import get_available_time_slots

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
    
    if MCP_AVAILABLE:
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
    else:
        # Fallback to direct call if MCP is not available (e.g. in some container environments)
        print("MCP not available, calling tool directly.")
        try:
            # Directly invoke the logic to find free time slots in the student's calendar
            slots = get_available_time_slots(student_id)
        except Exception as e:
            print(f"Error calling tool directly: {e}")
            slots = []
            
    # Prioritize assignments
    prioritized_assignments = prioritize_assignments(assignments, student_id)
    
    # Fetch real calendar events
    calendar_events = []
    try:
        from tools.calendar_mapper_tool import get_calendar_events
        calendar_events = get_calendar_events(student_id)
    except Exception as e:
        logger.error(f"Error fetching calendar events in planner: {e}")

    daily_plan = []
    # Use prioritized assignments for the plan
    for i, assignment in enumerate(prioritized_assignments[:len(slots)]):
        difficulty_tag = skill_profile.get(assignment.get("subject", ""), "on_track")
        daily_plan.append({
            "time": slots[i],
            "task_id": assignment["id"],
            "title": assignment["title"],
            "subject": assignment["subject"],
            "difficulty_tag": difficulty_tag,
            "due": assignment.get("due"), # Add due date to plan
            "state": assignment.get("state") # Add state to plan for color coding
        })
    
    return {
        "daily_plan": daily_plan,
        "prioritized_assignments": prioritized_assignments,
        "calendar_events": calendar_events
    }


def prioritize_assignments(assignments: List[Dict[str, Any]], student_id: str) -> List[Dict[str, Any]]:
    """
    Prioritize assignments using Gemini LLM based on complexity and due date.
    
    This function uses a Generative AI model to re-order the assignments.
    It considers:
    1. Urgency (Due date)
    2. Complexity (Subject difficulty)
    3. Student's current schedule (Calendar events)
    
    Args:
        assignments: List of assignments
        student_id: Student ID
        
    Returns:
        List of assignments sorted by priority
    """
    # Baseline sort by due date (soonest first) as a safe default
    assignments.sort(key=lambda x: x.get('due') or '9999-99-99')
    
    try:
        import google.generativeai as genai
        from datetime import datetime
        import time
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not found, skipping smart prioritization")
            return assignments
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Fetch real calendar events for context
        from tools.calendar_mapper_tool import get_calendar_events
        raw_events = get_calendar_events(student_id)
        
        # Format events for the prompt
        calendar_events = []
        for event in raw_events:
            summary = event.get('summary', 'Busy')
            start = event['start'].get('dateTime') or event['start'].get('date')
            end = event['end'].get('dateTime') or event['end'].get('date')
            # Simplify time for LLM
            if 'T' in start:
                start_time = start.split('T')[1][:5]
                end_time = end.split('T')[1][:5]
                calendar_events.append(f"{summary}: {start_time} - {end_time}")
            else:
                calendar_events.append(f"{summary}: All Day")
        
        if not calendar_events:
            calendar_events = ["No events scheduled for today."]
        
        # Log initial order
        logger.info(f"Initial top 3: {[a['title'] for a in assignments[:3]]}")
        

        # Optimization: Only send top 50 assignments to LLM to avoid context limit/timeout
        assignments_to_prioritize = assignments[:50]
        remaining_assignments = assignments[50:]
        
        # Simplify assignment objects for prompt
        simplified_assignments = []
        for a in assignments_to_prioritize:
            simple_a = {k: v for k, v in a.items() if k in ['id', 'title', 'subject', 'due']}
            # Truncate description if present
            if 'description' in a and a['description']:
                simple_a['description'] = a['description'][:200]
            simplified_assignments.append(simple_a)

        logger.info(f"Sending {len(simplified_assignments)} assignments to LLM for prioritization")
        
        prompt = f"""
        You are an expert student planner. Re-order the following assignments list to optimize for the student's schedule and success.
        
        Context:
        - Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        - Calendar Events today: {', '.join(calendar_events)}
        
        Assignments (currently sorted by due date):
        {json.dumps(simplified_assignments)}
        
        Task:
        Return the SAME list of assignments, but re-ordered based on "Priority to Start".
        
        Prioritization Rules:
        1.  **Urgency**: Assignments due today or tomorrow MUST be at the top.
        2.  **Complexity**: Among urgent tasks, put harder/longer ones first (while the student has energy).
        3.  **Quick Wins**: If a task is very short and due soon, slot it in to build momentum.
        
        Output Format:
        Return ONLY the valid JSON array of assignment objects. Do not wrap in markdown code blocks.
        """
        
        logger.info("Calling Gemini API...")
        start_time = time.time()
        response = model.generate_content(prompt)
        logger.info(f"Gemini API returned in {time.time() - start_time:.2f}s")
        
        # Extract JSON from response
        text = response.text
        # Clean up markdown if present
        text = text.replace('```json', '').replace('```', '').strip()
        
        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            prioritized_partial = json.loads(json_str)
            
            # Map back to full assignment objects (in case LLM dropped fields)
            # Create a dict of id -> full_assignment
            assignment_map = {a['id']: a for a in assignments_to_prioritize}
            
            final_list = []
            seen_ids = set()
            
            for p in prioritized_partial:
                if 'id' in p and p['id'] in assignment_map:
                    final_list.append(assignment_map[p['id']])
                    seen_ids.add(p['id'])
            
            # Append any missing from the prioritized set
            for a in assignments_to_prioritize:
                if a['id'] not in seen_ids:
                    final_list.append(a)
            
            # Append the remaining assignments that weren't sent to LLM
            final_list.extend(remaining_assignments)
            
            logger.info(f"Prioritized top 3: {[a['title'] for a in final_list[:3]]}")
            return final_list
        else:
            logger.warning("Could not parse LLM response for prioritization")
            return assignments
            
    except Exception as e:
        logger.error(f"Error in smart prioritization: {e}")
        return assignments



