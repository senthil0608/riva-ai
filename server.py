"""
FastAPI server for Riva AI - With Observability.
Handles student dashboard, parent summary, and guided learning requests.
"""
import time
from fastapi import FastAPI, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional, List

import os
from agents.aura_orchestrator_agent import run_aura_orchestrator
from agents.guided_learning_agent import run_guided_learning
from agents.aura_orchestrator_agent import run_aura_orchestrator
from agents.guided_learning_agent import run_guided_learning
from core.db import save_user, get_active_student, get_user
from core.auth_flow import get_auth_url, exchange_code

# Import observability
from core.observability import logger, tracer, metrics

# Configuration
# STUDENT_EMAILS and PARENT_EMAILS are now fetched from Firestore via get_active_student()

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


# Models
class AuraRequest(BaseModel):
    role: str  # "student" or "parent"
    action: str  # "get_dashboard", "get_parent_summary", "guided_hint"
    studentId: Optional[str] = None
    parentId: Optional[str] = None
    # For guided learning
    image: Optional[str] = None
    audio: Optional[str] = None
    question: Optional[str] = None
    auth_token: Optional[str] = None
    message: Optional[str] = None

class OnboardingRequest(BaseModel):
    student_name: str
    student_emails: List[str]
    parent_emails: List[str]

class AuthLoginRequest(BaseModel):
    email: str
    redirect_uri: str
    login_hint: Optional[str] = None

class AuthCallbackRequest(BaseModel):
    email: str
    code: str
    redirect_uri: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/user")
def get_user_status():
    """Check if there is an active student configured."""
    user = get_active_student()
    if user:
        return {"configured": True, "user": user}
    return {"configured": False}

@app.post("/api/onboarding")
def onboarding(req: OnboardingRequest):
    """Save initial user details."""
    # We use the first email as the primary ID
    primary_email = req.student_emails[0]
    data = {
        "student_name": req.student_name,
        "student_emails": req.student_emails,
        "parent_emails": req.parent_emails,
        "created_at": "now" # In real app use server time
    }
    if save_user(primary_email, data):
        return {"status": "success", "email": primary_email}
    return {"status": "error", "message": "Failed to save user"}

@app.post("/api/auth/login")
def auth_login(req: AuthLoginRequest):
    """Start OAuth flow."""
    # Use email as state to ensure we know who is authenticating
    url, state = get_auth_url(req.redirect_uri, req.login_hint, state=req.email)
    if url:
        return {"url": url, "state": state}
    return {"error": "Failed to generate auth URL"}

@app.post("/api/auth/callback")
def auth_callback(req: AuthCallbackRequest):
    """Exchange code for token."""
    creds = exchange_code(req.code, req.redirect_uri)
    if creds:
        # Save tokens to user profile
        if save_user(req.email, {"tokens": creds}):
            return {"status": "success"}
    return {"error": "Failed to authenticate"}

# New Secure Auth Endpoint
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

class VerifyRequest(BaseModel):
    role: str

@app.post("/api/auth/verify")
async def verify_token(req: VerifyRequest, request: Request):
    """Verify Google ID Token and check role access."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return {"error": "Missing or invalid Authorization header"}
    
    token = auth_header.split(" ")[1]
    
    try:
        # Verify Firebase ID Token
        decoded_token = auth.verify_id_token(token)
        email = decoded_token['email']
        
        # Get registered users
        user = get_active_student(email)
        if not user:
            return {"error": "User not found or not configured"}
            
        # Role Check
        if req.role == "student":
            # Allow ANY registered student email
            if email not in user.get('student_emails', []):
                return {"error": f"Access denied. Email {email} is not a registered student."}
        
        elif req.role == "parent":
            # Strict: Must be in parent_emails list
            if email not in user.get('parent_emails', []):
                return {"error": "Access denied. Email not registered as a parent."}
        
        else:
            return {"error": "Invalid role"}
            
        return {"status": "success", "email": email, "role": req.role}
        
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return {"error": "Invalid token"}

from firebase_admin import auth

async def verify_request_token(request: Request, required_role: str = None, token_override: str = None) -> dict:
    # Log headers for debugging
    # logger.info(f"DEBUG: Headers: {request.headers}")
    
    auth_header = request.headers.get("Authorization") or request.headers.get("X-Authorization")
    
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    elif token_override:
        token = token_override
        
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    try:
        # Verify Firebase ID Token
        decoded_token = auth.verify_id_token(token)
        email = decoded_token['email']
        
        user = get_active_student(email)
        if not user:
             raise HTTPException(status_code=400, detail="User not found or not configured")

        if required_role == "student":
            # Allow ANY registered student email
            if email not in user.get('student_emails', []):
                raise HTTPException(status_code=403, detail=f"Access denied. Email {email} is not a registered student.")
        elif required_role == "parent":
            if email not in user.get('parent_emails', []):
                raise HTTPException(status_code=403, detail=f"Access denied. Email {email} is not a registered parent.")
        
        return {"email": email, "role": required_role}
        
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid ID token")
    except auth.ExpiredIdTokenError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(status_code=500, detail="Authentication failed")

from fastapi import HTTPException

def background_dashboard_refresh(student_id: str):
    """
    Background task to run the orchestrator and save results to Firestore.
    """
    try:
        logger.info(f"Starting background refresh for {student_id}")
        # Run orchestrator
        result = run_aura_orchestrator(student_id)
        
        # Save result
        save_user(student_id, {
            "dashboard_cache": result,
            "dashboard_status": "completed",
            "dashboard_updated_at": "now" # In real app use server timestamp
        })
        logger.info(f"Background refresh completed for {student_id}")
    except Exception as e:
        logger.error(f"Background refresh failed for {student_id}: {e}")
        import traceback
        traceback.print_exc()
        save_user(student_id, {
            "dashboard_status": "error",
            "dashboard_error": str(e)
        })


@app.post("/api/aura")
async def aura_route(req: AuraRequest, request: Request, background_tasks: BackgroundTasks):
    """
    Main Aura endpoint that handles all requests from Next.js frontend.
    """
    # Verify Token and Enforce Role
    # We infer role from the request action/role
    if req.role not in ["student", "parent"]:
         return {"error": "Invalid role"}

    try:
        # This will raise HTTPException if invalid
        # Pass auth_token from body as fallback
        user_info = await verify_request_token(request, required_role=req.role, token_override=req.auth_token)
        logger.info(f"Authenticated user: {user_info['email']}")
    except HTTPException as e:
        logger.warning(f"Auth failed: {e.detail}")
        return {"error": e.detail}

    # Try to get student from DB if not provided
    student_id = req.studentId
    if not student_id:
        # If student, default to self
        if req.role == "student":
            student_id = user_info['email']
        else:
            # If parent, default to first student of this family
            user = get_active_student(user_info['email'])
            if user and user.get('student_emails'):
                student_id = user['student_emails'][0]
    
    logger.info(f"Processing request for student_id: {student_id}")
    
    if not student_id:
         return {"error": "No student configured. Please complete onboarding."}

    # Student Dashboard - Async Start
    if req.role == "student" and req.action == "start_dashboard_refresh":
        # Set status to processing
        save_user(student_id, {"dashboard_status": "processing"})
        # Add background task
        background_tasks.add_task(background_dashboard_refresh, student_id)
        return {"status": "started"}

    # Student Dashboard - Check Status / Get Data
    if req.role == "student" and req.action == "get_dashboard":
        user = get_active_student(student_id)
        if not user:
             return {"error": "User not found"}
             
        status = user.get("dashboard_status")
        
        if status == "processing":
             return {"status": "processing"}
        elif status == "completed":
             # Return cached data + status
             data = user.get("dashboard_cache", {})
             data["status"] = "completed"
             return data
        elif status == "error":
             return {"status": "error", "error": user.get("dashboard_error")}
        else:
             # Not started yet
             return {"status": "not_started"}
    
    # Legacy Sync Call (Optional: keep for fallback or remove?)
    # Keeping it removed/replaced by async flow logic above.
    # If client sends "get_dashboard" without start, it will hit the logic above 
    # and return "not_started" or old cache.

    
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
        
    # Chat
    if req.role == "student" and req.action == "chat":
        from agents.aura_chat_agent import run_aura_chat
        result = run_aura_chat(student_id, req.message)
        return result
    
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
            "/api/aura": "Main agent endpoint (POST)",
            "/health": "Health check (GET)",
            "/metrics": "Prometheus metrics (GET)",
            "/docs": "API documentation (GET)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Riva AI FastAPI Server with Observability...")
    port = int(os.getenv("PORT", 8000))
    logger.info(f"📍 Listening on http://0.0.0.0:{port}")
    logger.info(f"📖 API docs: http://0.0.0.0:{port}/docs")
    logger.info(f"📊 Metrics: http://0.0.0.0:{port}/metrics")
    logger.info(f"🔗 Next.js frontend should connect to http://0.0.0.0:{port}/api/aura")
    uvicorn.run(app, host="0.0.0.0", port=port)
