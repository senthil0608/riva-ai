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
    import os
    import google.generativeai as genai
    from core.observability import logger

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found for OCR")
        return ""

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        # If image is a path, read it
        if isinstance(image, str) and os.path.exists(image):
            # Upload file to Gemini
            myfile = genai.upload_file(image)
            
            response = model.generate_content([
                "Extract all text from this image. Return ONLY the extracted text.",
                myfile
            ])
            return response.text.strip()
            
        else:
            logger.warning("Direct bytes/base64 not fully implemented in this snippet without temp file.")
            return ""

    except Exception as e:
        logger.error(f"Error in OCR: {e}")
        return ""
