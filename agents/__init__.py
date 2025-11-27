"""
Agents package - Google ADK agents with fallback functions.
"""

from .classroom_sync_agent import run_classroom_sync
from .skill_mastery_agent import run_skill_mastery
from .daily_planner_agent import run_daily_planner
from .guided_learning_agent import run_guided_learning
from .parent_insight_agent import run_parent_insight
from .aura_orchestrator_agent import run_aura_orchestrator

__all__ = [
    # Fallback functions
    'run_classroom_sync',
    'run_skill_mastery',
    'run_daily_planner',
    'run_guided_learning',
    'run_parent_insight',
    'run_aura_orchestrator',
]
