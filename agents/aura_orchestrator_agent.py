"""
Aura Orchestrator Agent - Google ADK version.
Central brain that coordinates all other agents using ADK Workflow.
"""
from typing import Dict, Any, Optional
import os
import uuid
from datetime import datetime

from core.models import WorkflowState, AgentState
from core.db import save_workflow_state, get_workflow_state

from .classroom_sync_agent import run_classroom_sync
from .skill_mastery_agent import run_skill_mastery
from .daily_planner_agent import run_daily_planner
from .parent_insight_agent import run_parent_insight

def run_aura_orchestrator(student_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Orchestrate all agents to create a complete student plan.
    Supports Pause/Resume via Firestore state persistence.
    
    Args:
        student_id: The student's ID
        session_id: Optional session ID to resume. If None, creates new session.
        
    Returns:
        Dictionary with all results (assignments, daily_plan, skill_profile, parent_summary)
    """
    print(f"[Aura] Starting orchestration for student: {student_id}")
    from core.observability import logger
    logger.info(f"Orchestrator called for student: {student_id}")
    
    # 1. Initialize or Load State
    if session_id:
        state_data = get_workflow_state(session_id)
        if state_data:
            state = WorkflowState(**state_data)
            logger.info(f"Resuming session {session_id} from state {state.current_step}")
        else:
            logger.warning(f"Session {session_id} not found. Starting new session.")
            session_id = str(uuid.uuid4())
            state = WorkflowState(session_id=session_id, student_id=student_id)
    else:
        session_id = str(uuid.uuid4())
        state = WorkflowState(session_id=session_id, student_id=student_id)
        logger.info(f"Started new session {session_id}")

    # Helper to save state
    def checkpoint(new_step: AgentState):
        state.current_step = new_step
        state.last_updated = datetime.now()
        save_workflow_state(session_id, state.model_dump(mode='json'))
        logger.info(f"Checkpoint saved: {new_step}")

    # Helper to check pause
    def check_pause():
        # Reload state to check for external pause signal
        current_db_state = get_workflow_state(session_id)
        if current_db_state and current_db_state.get('pause_requested'):
            state.pause_requested = True
            state.current_step = AgentState.PAUSED
            checkpoint(AgentState.PAUSED)
            logger.info("Pause requested. Stopping execution.")
            return True
        return False

    try:
        # STEP 1: SYNC (Get Assignments)
        if state.current_step in [AgentState.IDLE, AgentState.SYNCING]:
            if check_pause(): return state.model_dump()
            
            checkpoint(AgentState.SYNCING)
            state.assignments = run_classroom_sync(student_id)
            print(f"[Aura] Retrieved {len(state.assignments)} assignments")
            
            # Move to next step
            checkpoint(AgentState.ANALYZING)

        # STEP 2: ANALYZE (Skill Profile)
        if state.current_step == AgentState.ANALYZING:
            if check_pause(): return state.model_dump()
            
            state.skill_profile = run_skill_mastery(student_id)
            print(f"[Aura] Skill profile: {list(state.skill_profile.keys())}")
            
            checkpoint(AgentState.PLANNING)

        # STEP 3: PLAN (Daily Schedule)
        if state.current_step == AgentState.PLANNING:
            if check_pause(): return state.model_dump()
            
            planner_result = run_daily_planner(student_id, state.assignments, state.skill_profile)
            state.daily_plan = planner_result["daily_plan"]
            state.calendar_events = planner_result.get("calendar_events", [])
            print(f"[Aura] Created plan with {len(state.daily_plan)} tasks")
            
            checkpoint(AgentState.REPORTING)

        # STEP 4: REPORT (Parent Insight)
        if state.current_step == AgentState.REPORTING:
            if check_pause(): return state.model_dump()
            
            state.parent_insight = run_parent_insight(
                student_id, 
                state.assignments, 
                state.daily_plan, 
                state.skill_profile
            )
            
            checkpoint(AgentState.COMPLETED)

    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        state.error = str(e)
        checkpoint(AgentState.FAILED)
        raise

    return state.model_dump()



