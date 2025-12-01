"""
Parent Insight Agent - Google ADK version.
Generates summaries and insights for parents using Gemini LLM.
"""
from typing import Dict, Any, List
import os

try:
    from google.adk import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    print("Warning: google-adk not installed. Using fallback mode.")


from core.models import Assignment, DailyPlanItem, SkillProfile, ParentInsight

def run_parent_insight(
    student_id: str,
    assignments: List[Assignment],
    daily_plan: List[DailyPlanItem],
    skill_profile: SkillProfile
) -> ParentInsight:
    """
    Generate a summary for parents.
    Fallback function when ADK not available.
    
    Args:
        student_id: The student's ID
        assignments: List of Assignment objects
        daily_plan: Student's daily plan (List[DailyPlanItem])
        skill_profile: Student's skill levels
        
    Returns:
        ParentInsight object with summary and stress level
    """
    num_assignments = len(assignments)
    num_planned = len(daily_plan)
    
    if num_planned <= 2:
        stress_level = "Low"
    elif num_planned <= 4:
        stress_level = "Moderate"
    else:
        stress_level = "High"
    
    summary_text = f"Total assignments: {num_assignments}\nTasks planned for today: {num_planned}\nEstimated stress level: {stress_level}"
    
    return ParentInsight(
        summary_text=summary_text,
        stress_level=stress_level
    )



