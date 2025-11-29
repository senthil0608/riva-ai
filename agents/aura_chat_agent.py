"""
Aura Chat Agent.
Handles natural language queries from the student dashboard using Gemini.
"""
from typing import Dict, Any
import os
import google.generativeai as genai
from core.observability import logger
from .classroom_sync_agent import run_classroom_sync
from .daily_planner_agent import run_daily_planner
from .skill_mastery_agent import run_skill_mastery

def run_aura_chat(student_id: str, message: str) -> Dict[str, Any]:
    """
    Process a chat message from the student.
    
    Args:
        student_id: The student's ID
        message: The user's message
        
    Returns:
        Dictionary with the response text and optional data updates
    """
    logger.info(f"Aura Chat: Processing message '{message}' for {student_id}")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"response": "I'm sorry, I can't connect to my brain right now (API Key missing)."}
        
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-flash-latest')
    
    # 1. Gather Context
    # We fetch assignments to give the LLM context about what the student has to do.
    # This might be slow, but ensures up-to-date info.
    try:
        classroom_result = run_classroom_sync(student_id)
        assignments = classroom_result.get("assignments", [])
        
        # Get calendar events if possible (reusing logic from planner would be better, but for now just assignments)
        # We could also fetch the current plan if we wanted to be very smart.
        
        context_str = f"Student has {len(assignments)} assignments."
        if assignments:
            top_5 = assignments[:5]
            context_str += f" Top 5 upcoming: {', '.join([a['title'] + ' (Due: ' + (a.get('due') or 'No date') + ')' for a in top_5])}."
            
    except Exception as e:
        logger.error(f"Error fetching context for chat: {e}")
        context_str = "Could not fetch current assignments."

    # 2. Generate Response
    prompt = f"""
    You are Aura, an intelligent and encouraging academic coach for a student.
    
    Student Context:
    {context_str}
    
    User Query: "{message}"
    
    Your Goal:
    Respond to the user's query in a helpful, friendly, and concise way.
    - If they ask for a study plan, tell them you've organized their dashboard with today's priorities.
    - If they ask about homework, summarize their top tasks.
    - If they are stressed, offer encouragement.
    - Keep the response under 50 words if possible.
    
    Response:
    """
    
    try:
        response = model.generate_content(prompt)
        reply_text = response.text.strip()
        return {"response": reply_text}
    except Exception as e:
        logger.error(f"Error generating chat response: {e}")
        return {"response": "I'm having trouble thinking right now. Please try again."}
