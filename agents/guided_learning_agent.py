"""
Guided Learning Agent - Google ADK version.
Provides homework hints using Gemini LLM with OCR and speech-to-text.
"""
from typing import Dict, Any, Optional
import os
import sys

# Import MCP
import asyncio
import os
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import observability
from core.observability import logger, tracer




def run_guided_learning(
    student_id: str,
    image: Optional[str] = None,
    audio: Optional[str] = None,
    question: Optional[str] = None
) -> Dict[str, Any]:
    """
    Provide a hint for a homework problem.
    Fallback function when ADK not available.
    
    Args:
        student_id: The student's ID
        image: Image of the problem (optional)
        audio: Audio of the question (optional)
        question: Text question (optional)
        
    Returns:
        Dictionary with hint and problem text
    """
    problem_text = question or ""
    
    if image:
        async def fetch_ocr_mcp():
            server_params = StdioServerParameters(
                command=sys.executable,
                args=["-m", "tools.ocr_server"],
                env=os.environ.copy()
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    tool_name = "extract_text_from_image"
                    tool_args = {"image_data": "..."} # Truncate for log
                    
                    logger.log_tool_call(tool_name, tool_args, "guided_learning")
                    
                    with tracer.trace_span(f"tool.{tool_name}") as span:
                        start_ts = time.time()
                        try:
                            result = await session.call_tool(
                                tool_name,
                                arguments={"image_data": image}
                            )
                            duration = (time.time() - start_ts) * 1000
                            logger.log_tool_result(tool_name, duration, True)
                            
                            if result.content and hasattr(result.content[0], "text"):
                                return result.content[0].text
                            return ""
                        except Exception as e:
                            duration = (time.time() - start_ts) * 1000
                            logger.log_tool_result(tool_name, duration, False, str(e))
                            raise
        try:
            problem_text = asyncio.run(fetch_ocr_mcp())
        except Exception as e:
            print(f"Error calling MCP OCR tool: {e}")
            
    elif audio:
        async def fetch_audio_mcp():
            server_params = StdioServerParameters(
                command=sys.executable,
                args=["-m", "tools.speech_to_text_server"],
                env=os.environ.copy()
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    tool_name = "transcribe_audio"
                    tool_args = {"audio_data": "..."} # Truncate for log
                    
                    logger.log_tool_call(tool_name, tool_args, "guided_learning")
                    
                    with tracer.trace_span(f"tool.{tool_name}") as span:
                        start_ts = time.time()
                        try:
                            result = await session.call_tool(
                                tool_name,
                                arguments={"audio_data": audio}
                            )
                            duration = (time.time() - start_ts) * 1000
                            logger.log_tool_result(tool_name, duration, True)
                            
                            if result.content and hasattr(result.content[0], "text"):
                                return result.content[0].text
                            return ""
                        except Exception as e:
                            duration = (time.time() - start_ts) * 1000
                            logger.log_tool_result(tool_name, duration, False, str(e))
                            raise
        try:
            problem_text = asyncio.run(fetch_audio_mcp())
        except Exception as e:
            print(f"Error calling MCP Audio tool: {e}")
    
    hint = "Start by identifying what the question is asking. Then write down the known values and see which operation you might use."
    
    return {
        "problem_text": problem_text,
        "hint": hint
    }



