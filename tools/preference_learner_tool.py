"""
Preference Learner Tool.
Analyzes student interactions to extract and save learning preferences.
"""
import os
import json
import re
from typing import Dict, Any, List
from core.db import save_user, get_user
from core.observability import logger

def learn_preferences_from_chat(student_id: str, message: str, chat_history: List[Dict[str, str]] = []) -> Dict[str, Any]:
    """
    Analyze chat to extract learning preferences and update the user profile.
    
    Args:
        student_id: The student's ID (email)
        message: The latest message from the student
        chat_history: Recent chat context
        
    Returns:
        Dictionary of extracted preferences
    """
    logger.info(f"Analyzing preferences for {student_id}")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("No API key for preference learning")
        return {}

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Construct prompt
        history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history[-5:]])
        
        prompt = f"""
        You are an expert educational psychologist. Analyze the following student interaction to detect learning preferences, habits, or constraints.
        
        Student ID: {student_id}
        Recent Chat:
        {history_text}
        Latest Message: "{message}"
        
        Goal: Extract ANY new information about:
        1. Preferred subjects (e.g., "I love math")
        2. Disliked subjects (e.g., "I hate writing")
        3. Energy levels/Time preferences (e.g., "I'm tired", "I work best at night")
        4. Learning style (e.g., "I need examples", "I like videos")
        
        Output:
        Return a JSON object with a "preferences" key containing key-value pairs of NEW insights. 
        If nothing new is found, return {{"preferences": {{}}}}.
        
        Example:
        {{
            "preferences": {{
                "math_sentiment": "positive",
                "preferred_time": "evening",
                "focus_duration": "short"
            }}
        }}
        """
        
        response = model.generate_content(prompt)
        text = response.text.replace('```json', '').replace('```', '').strip()
        
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group(0))
            new_prefs = result.get("preferences", {})
            
            if new_prefs:
                logger.info(f"Extracted new preferences: {new_prefs}")
                
                # Fetch existing user to merge deeply if needed, 
                # but Firestore merge=True handles top-level keys.
                # We want to merge into a 'preferences' map.
                
                # 1. Get current preferences
                user = get_user(student_id)
                current_prefs = user.get('preferences', {}) if user else {}
                
                # 2. Update with new ones
                current_prefs.update(new_prefs)
                
                # 3. Save back
                save_user(student_id, {"preferences": current_prefs})
                return new_prefs
                
        return {}

    except Exception as e:
        logger.error(f"Error in preference learning: {e}")
        return {}
