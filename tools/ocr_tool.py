"""
OCR tool - ADK version with Gemini Vision.
Extracts text from images using Google's multimodal capabilities.
"""
from typing import Union


def extract_text_from_image(image: Union[str, bytes]) -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        image: Image as base64 string, file path, or bytes
        
    Returns:
        Extracted text from the image
    """
    # TODO: Implement Gemini Vision API call
    # For now, return mock data
    return "Solve 3x + 5 = 20"
