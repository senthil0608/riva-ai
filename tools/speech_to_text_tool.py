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
    # TODO: Implement Google Cloud Speech-to-Text API call
    # For now, return mock data
    return "How do I solve 3x plus 5 equals 20"
