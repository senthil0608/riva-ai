"""
Aura Orchestrator Agent - Google ADK version.
Central brain that coordinates all other agents using ADK Workflow.
"""
from typing import Dict, Any
import os

from .classroom_sync_agent import run_classroom_sync
from .skill_mastery_agent import run_skill_mastery
from .daily_planner_agent import run_daily_planner
from .parent_insight_agent import run_parent_insight




def run_aura_orchestrator(student_id: str) -> Dict[str, Any]:
    """
    Orchestrate all agents to create a complete student plan.
    Fallback function when ADK not available.
    
    Args:
        student_id: The student's ID
        
    Returns:
        Dictionary with all results (assignments, daily_plan, skill_profile, parent_summary)
    """
    print(f"[Aura] Starting orchestration for student: {student_id}")
    from core.observability import logger
    logger.info(f"Orchestrator called for student: {student_id}")
    
    # 1. Get assignments
    classroom_result = run_classroom_sync(student_id)
    assignments = classroom_result["assignments"]
    print(f"[Aura] Retrieved {len(assignments)} assignments")
    
    # 2. Get skill profile
    skill_result = run_skill_mastery(student_id)
    skill_profile = skill_result["skill_profile"]
    print(f"[Aura] Skill profile: {list(skill_profile.keys())}")
    
    # 3. Create daily plan
    planner_result = run_daily_planner(student_id, assignments, skill_profile)
    daily_plan = planner_result["daily_plan"]
    print(f"[Aura] Created plan with {len(daily_plan)} tasks")
    
    # 4. Generate parent summary
    parent_result = run_parent_insight(student_id, assignments, daily_plan, skill_profile)
    
    # Use prioritized assignments if available, otherwise fallback to original
    final_assignments = planner_result.get("prioritized_assignments", assignments)
    calendar_events = planner_result.get("calendar_events", [])
    
    return {
        "assignments": final_assignments,
        "skill_profile": skill_profile,
        "daily_plan": daily_plan,
        "parent_summary": parent_result,
        "calendar_events": calendar_events
    }



