"""
FastAPI server for Riva AI - With Observability.
Handles student dashboard, parent summary, and guided learning requests.
"""
import time
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional

from agents import (
    run_aura_orchestrator,
    run_guided_learning,
)

# Import observability
from core.observability import logger, tracer, metrics

app = FastAPI(title="Riva AI API", version="2.0.0")

# Allow calls from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Observability middleware
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Add logging, tracing, and metrics to all requests."""
    start_time = time.time()
    
    # Log request
    logger.log_api_request(
        endpoint=request.url.path,
        method=request.method,
        student_id=None  # Could extract from request if needed
    )
    
    # Trace request
    with tracer.trace_api_call(request.url.path, request.method):
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            logger.log_error_with_context(e, {
                "endpoint": request.url.path,
                "method": request.method
            })
            metrics.record_error(type(e).__name__, "api")
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            metrics.record_api_request(
                endpoint=request.url.path,
                method=request.method,
                status_code=status_code if 'status_code' in locals() else 500,
                duration_seconds=duration
            )
            
            # Log response
            logger.log_api_response(
                endpoint=request.url.path,
                status_code=status_code if 'status_code' in locals() else 500,
                duration_ms=duration * 1000
            )
    
    return response


# Request model
class AuraRequest(BaseModel):
    role: str
    action: str
    studentId: Optional[str] = None
    question: Optional[str] = None
    image: Optional[str] = None
    audio: Optional[str] = None


@app.post("/aura")
async def aura_route(req: AuraRequest):
    """
    Main Aura endpoint that handles all requests from Next.js frontend.
    
    Supported actions:
    - Student dashboard: role="student", action="get_dashboard"
    - Parent summary: role="parent", action="get_parent_summary"
    - Guided hint: role="student", action="guided_hint"
    """
    student_id = req.studentId or "demo-student"
    
    # Student Dashboard
    if req.role == "student" and req.action == "get_dashboard":
        result = run_aura_orchestrator(student_id)
        return result
    
    # Guided Learning (photo + voice)
    if req.role == "student" and req.action == "guided_hint":
        result = run_guided_learning(
            student_id=student_id,
            image=req.image,
            audio=req.audio,
            question=req.question
        )
        return result
    
    # Parent Summary
    if req.role == "parent" and req.action == "get_parent_summary":
        # Get full orchestration result
        full_result = run_aura_orchestrator(student_id)
        return {
            "parent_summary": full_result["parent_summary"]
        }
    
    return {"error": "Invalid request"}


@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint."""
    metrics_data = metrics.get_metrics()
    return Response(
        content=metrics_data,
        media_type="text/plain; version=0.0.4"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Riva AI API",
        "version": "2.0.0",
        "observability": {
            "logging": "enabled",
            "tracing": "enabled",
            "metrics": "enabled"
        }
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Riva AI API",
        "version": "2.0.0",
        "description": "Google ADK with Observability",
        "endpoints": {
            "/aura": "Main agent endpoint (POST)",
            "/health": "Health check (GET)",
            "/metrics": "Prometheus metrics (GET)",
            "/docs": "API documentation (GET)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Riva AI FastAPI Server with Observability...")
    logger.info("📍 Listening on http://localhost:8000")
    logger.info("📖 API docs: http://localhost:8000/docs")
    logger.info("📊 Metrics: http://localhost:8000/metrics")
    logger.info("🔗 Next.js frontend should connect to http://localhost:8000/aura")
    uvicorn.run(app, host="0.0.0.0", port=8000)
