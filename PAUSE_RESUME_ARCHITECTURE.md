# Pause/Resume Agent Architecture

This document outlines the architecture and implementation of the **Pause and Resume** functionality in the Aura Agent system. This capability allows long-running agent workflows to be interrupted (e.g., by user action or system shutdown) and resumed later without losing progress.

## 1. High-Level Overview

The system uses a **State Machine** pattern implemented in the `AuraOrchestratorAgent`. The workflow is divided into discrete steps. After each step completes, the system:
1.  **Checkpoints**: Saves the current state (including all data gathered so far) to a persistent database (Firestore).
2.  **Checks for Pause**: Looks for a "pause signal" in the database. If found, execution stops immediately.

When the Orchestrator is called again with the same `session_id`, it loads the saved state and **skips** any steps that are already marked as completed, resuming execution from the last successful checkpoint.

## 2. Architecture Components

### A. Data Models (`core/models.py`)
We use strict **Pydantic models** to define the state and data structures. This ensures data integrity during serialization/deserialization.

*   **`WorkflowState`**: The root object persisted to the DB.
    *   `session_id` (str): Unique identifier for the run.
    *   `current_step` (Enum): Current stage (`SYNCING`, `ANALYZING`, `PLANNING`, `REPORTING`, `COMPLETED`).
    *   `assignments` (List[Assignment]): Data from Classroom Sync.
    *   `skill_profile` (SkillProfile): Data from Skill Mastery.
    *   `daily_plan` (List[DailyPlanItem]): Data from Daily Planner.
    *   `pause_requested` (bool): Flag to trigger a pause.

### B. Database Layer (`core/db.py`)
Two functions handle state persistence in Firestore:
*   `save_workflow_state(session_id, state_data)`: Upserts the state document.
*   `get_workflow_state(session_id)`: Retrieves the state document.

**Firestore Collection**: `workflow_states`

### C. Orchestrator (`agents/aura_orchestrator_agent.py`)
The `run_aura_orchestrator` function is the core engine.

**Logic Flow:**
1.  **Initialization**:
    *   Input: `student_id`, optional `session_id`.
    *   If `session_id` is provided, load state from DB.
    *   If not, create a new session and state.
2.  **Step Execution (Re-entrant)**:
    *   **Step 1: Sync**: Checks if `state.current_step < SYNCING`. If yes, runs `ClassroomSyncAgent`, updates state, saves checkpoint.
    *   **Step 2: Analyze**: Checks if `state.current_step < ANALYZING`. If yes, runs `SkillMasteryAgent`, updates state, saves checkpoint.
    *   **Step 3: Plan**: Checks if `state.current_step < PLANNING`. If yes, runs `DailyPlannerAgent`, updates state, saves checkpoint.
    *   **Step 4: Report**: Checks if `state.current_step < REPORTING`. If yes, runs `ParentInsightAgent`, updates state, saves checkpoint.

## 3. How to Use

### Starting a New Session
Call the orchestrator with just the student ID.
```python
from agents.aura_orchestrator_agent import run_aura_orchestrator
result = run_aura_orchestrator("student@example.com")
session_id = result['session_id']
```

### Pausing a Session
Update the Firestore document for the session to set `pause_requested = True`.
```python
# In a separate process or API endpoint
db.collection("workflow_states").document(session_id).update({"pause_requested": True})
```
The Orchestrator checks this flag before starting each new step. If true, it saves the state as `PAUSED` and returns.

### Resuming a Session
Call the orchestrator with the existing `session_id`.
```python
# Resume
result = run_aura_orchestrator("student@example.com", session_id="existing-session-id")
```
The system will detect the existing state and resume from where it left off.

## 4. Code Locations

| Component | File Path | Description |
| :--- | :--- | :--- |
| **Models** | `core/models.py` | Pydantic definitions for `WorkflowState`, `Assignment`, etc. |
| **DB Access** | `core/db.py` | Firestore save/load functions. |
| **Orchestrator** | `agents/aura_orchestrator_agent.py` | Main state machine logic. |
| **Sub-Agents** | `agents/*_agent.py` | Updated to use Pydantic models. |
