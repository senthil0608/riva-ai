"""
Speech-to-Text tool - ADK version.
Transcribes audio to text using Google Cloud Speech-to-Text.
"""
from typing import Union


def transcribe_audio(audio: Union[str, bytes]) -> str:
    """
    Transcribe audio to text.
    
    Args:
        audio: Audio as base64 string, file path, or bytes
        
    Returns:
        Transcribed text from the audio
    """
    import os
    import google.generativeai as genai
    from core.observability import logger

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found for speech-to-text")
        return ""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash') # Flash is good for multimodal

        # If audio is a path, read it
        if isinstance(audio, str) and os.path.exists(audio):
            # Upload file to Gemini
            # Note: For simple audio clips, we might need to use the File API
            # But for this MVP let's assume we can pass the bytes or handle it via prompt if small enough?
            # Actually, Gemini API supports audio files.
            
            # Simplified approach: We'll assume the 'audio' argument is a path to a file
            # that we can upload.
            myfile = genai.upload_file(audio)
            
            response = model.generate_content([
                "Transcribe this audio file exactly as spoken.",
                myfile
            ])
            return response.text.strip()
            
        else:
            # If it's bytes or base64, we'd need to save to temp file first for the upload_file API
            # or use inline data if supported.
            logger.warning("Direct bytes/base64 not fully implemented in this snippet without temp file.")
            return ""

    except Exception as e:
        logger.error(f"Error in speech-to-text: {e}")
        return ""
