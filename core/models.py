from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field

class AssignmentState(str, Enum):
    PUBLISHED = "PUBLISHED"
    TURNED_IN = "TURNED_IN"
    RETURNED = "RETURNED"
    LATE = "LATE"
    CREATED = "CREATED"
    NEW = "NEW"
    RECLAIMED_BY_STUDENT = "RECLAIMED_BY_STUDENT"
    DRAFT = "DRAFT"
    UNKNOWN = "UNKNOWN"
    
    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

class Assignment(BaseModel):
    id: str
    title: str
    subject: str
    due: Optional[str] = None
    state: AssignmentState = AssignmentState.UNKNOWN
    description: Optional[str] = ""
    course_id: Optional[str] = None

class SkillLevel(str, Enum):
    NEEDS_SUPPORT = "needs_support"
    ON_TRACK = "on_track"
    STRONG = "strong"
    UNKNOWN = "unknown"

# SkillProfile is a mapping of Subject -> SkillLevel
SkillProfile = Dict[str, SkillLevel]

class DailyPlanItem(BaseModel):
    time: str
    task_id: str
    title: str
    subject: str
    difficulty_tag: str
    due: Optional[str] = None
    state: Optional[str] = None

class ParentInsight(BaseModel):
    summary_text: str
    stress_level: str

class AgentState(str, Enum):
    IDLE = "IDLE"
    SYNCING = "SYNCING"
    ANALYZING = "ANALYZING"
    PLANNING = "PLANNING"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"
    PAUSED = "PAUSED"
    FAILED = "FAILED"

class WorkflowState(BaseModel):
    session_id: str
    student_id: str
    current_step: AgentState = AgentState.IDLE
    assignments: List[Assignment] = Field(default_factory=list)
    skill_profile: SkillProfile = Field(default_factory=dict)
    daily_plan: List[DailyPlanItem] = Field(default_factory=list)
    parent_insight: Optional[ParentInsight] = None
    calendar_events: List[str] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    pause_requested: bool = False
    error: Optional[str] = None
