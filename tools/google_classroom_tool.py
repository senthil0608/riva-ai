"""
Google Classroom tool - Real API integration.
Fetches student assignments from Google Classroom using the official API.
"""
from typing import List, Dict, Any, Optional
import os
import pickle
from datetime import datetime

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False
    print("Warning: Google API libraries not installed. Using mock data.")

# Import observability
from core.observability import logger, tracer, metrics

# Google Classroom API scopes
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.students.readonly',
    'https://www.googleapis.com/auth/classroom.rosters.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.students.readonly'
]


from core.db import get_user

def get_classroom_service(student_email: Optional[str] = None):
    """
    Authenticate and return Google Classroom API service.
    
    Prioritizes credentials stored in Firestore.
    Falls back to local pickle files for backward compatibility.
    
    Args:
        student_email: The email of the student to authenticate.
    
    Returns:
        Google Classroom API service object or None if auth fails
    """
    if not GOOGLE_API_AVAILABLE:
        return None
    
    creds = None
    
    # 1. Try Firestore first
    if student_email:
        try:
            user_data = get_user(student_email)
            if user_data and 'tokens' in user_data:
                token_data = user_data['tokens']
                creds = Credentials(
                    token=token_data.get('token'),
                    refresh_token=token_data.get('refresh_token'),
                    token_uri=token_data.get('token_uri'),
                    client_id=token_data.get('client_id'),
                    client_secret=token_data.get('client_secret'),
                    scopes=token_data.get('scopes')
                )
                logger.info(f"Loaded credentials from Firestore for {student_email}")
        except Exception as e:
            logger.error(f"Error loading credentials from Firestore: {e}")

    # 2. Fallback to local pickle (legacy) - REMOVED
    # User requested strict Firestore usage.
    if not creds:
        logger.warning(f"No credentials found for {student_email} in Firestore.")
        return None
    
    try:
        service = build('classroom', 'v1', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Failed to build Classroom service: {e}")
        return None


@tracer.trace_tool("list_assignments_for_student")
def list_assignments_for_student(student_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all assignments for a student from Google Classroom.
    
    Args:
        student_id: The student's ID (email or Google ID)
        
    Returns:
        List of assignments with id, title, subject, and due date
    """
    logger.log_tool_call("list_assignments_for_student", {"student_id": student_id})
    
    with metrics.track_tool("list_assignments_for_student"):
        try:
            service = get_classroom_service(student_id)
            
            if not service:
                # Fallback to mock data
                logger.warning("Using mock data for Google Classroom")
                return _get_mock_assignments()
            
            assignments = []
            
            # Get all courses for the student
            logger.debug("Fetching courses for student", student_id=student_id)
            courses_result = service.courses().list(
                studentId=student_id,
                courseStates=['ACTIVE']
            ).execute()
            
            courses = courses_result.get('courses', [])
            logger.info(f"Found {len(courses)} active courses", student_id=student_id)
            
            # Get coursework for each course
            for course in courses:
                course_id = course['id']
                course_name = course['name']
                
                try:
                    coursework_result = service.courses().courseWork().list(
                        courseId=course_id,
                        orderBy='dueDate desc'
                    ).execute()
                    
                    coursework_items = coursework_result.get('courseWork', [])
                    
                    # Fetch student submissions to check status
                    submissions_result = service.courses().courseWork().studentSubmissions().list(
                        courseId=course_id,
                        courseWorkId='-', # '-' means all coursework
                        userId=student_id
                    ).execute()
                    submissions = submissions_result.get('studentSubmissions', [])
                    
                    # Create a map of courseworkId -> state
                    submission_states = {s['courseWorkId']: s['state'] for s in submissions}
                    
                    for item in coursework_items:
                        # Check submission state
                        state = submission_states.get(item['id'])
                        # We now include all states (TURNED_IN, RETURNED, etc.)

                        # Parse due date
                        due_date = None
                        if 'dueDate' in item:
                            due_data = item['dueDate']
                            due_date = f"{due_data['year']}-{due_data['month']:02d}-{due_data['day']:02d}"
                        
                        assignment = {
                            "id": item['id'],
                            "title": item['title'],
                            "subject": course_name,
                            "due": due_date or "No due date",
                            "description": item.get('description', ''),
                            "state": state or item.get('state', 'PUBLISHED'),
                            "course_id": course_id
                        }
                        assignments.append(assignment)
                
                except HttpError as e:
                    logger.warning(
                        f"Could not fetch coursework for course {course_name}",
                        error=str(e)
                    )
                    continue
            
            logger.info(
                f"Retrieved {len(assignments)} assignments",
                student_id=student_id,
                num_courses=len(courses)
            )
            
            metrics.record_tool_call("list_assignments_for_student", 0, "success")
            return assignments
            
        except HttpError as e:
            logger.error(
                "Google Classroom API error",
                error=str(e),
                student_id=student_id
            )
            metrics.record_error("HttpError", "tool.list_assignments")
            # Fallback to mock data
            return _get_mock_assignments()
        
        except Exception as e:
            logger.error(
                "Unexpected error fetching assignments",
                error=str(e),
                error_type=type(e).__name__,
                student_id=student_id
            )
            metrics.record_error(type(e).__name__, "tool.list_assignments")
            # Fallback to mock data
            return _get_mock_assignments()


def _get_mock_assignments() -> List[Dict[str, Any]]:
    """Return mock assignments for development/testing."""
    return [
        {
            "id": "mock_a1",
            "title": "Math Worksheet 5",
            "subject": "Math",
            "due": "2025-11-26",
            "description": "Complete problems 1-20",
            "state": "PUBLISHED",
            "course_id": "mock_course_1"
        },
        {
            "id": "mock_a2",
            "title": "Reading Log - Chapter 3",
            "subject": "ELA",
            "due": "2025-11-27",
            "description": "Read and summarize chapter 3",
            "state": "PUBLISHED",
            "course_id": "mock_course_2"
        },
        {
            "id": "mock_a3",
            "title": "Science Lab Prep",
            "subject": "Science",
            "due": "2025-11-28",
            "description": "Prepare for lab experiment",
            "state": "PUBLISHED",
            "course_id": "mock_course_3"
        }
    ]


def get_student_submissions(student_id: str, course_id: str, coursework_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a student's submission for a specific assignment.
    
    Args:
        student_id: The student's ID
        course_id: The course ID
        coursework_id: The coursework/assignment ID
        
    Returns:
        Submission data or None
    """
    try:
        service = get_classroom_service(student_id)
        if not service:
            return None
        
        submission = service.courses().courseWork().studentSubmissions().get(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=student_id
        ).execute()
        
        return {
            "id": submission['id'],
            "state": submission.get('state', 'CREATED'),
            "late": submission.get('late', False),
            "assigned_grade": submission.get('assignedGrade'),
            "draft_grade": submission.get('draftGrade'),
            "submission_history": submission.get('submissionHistory', [])
        }
    
    except Exception as e:
        logger.error(f"Error fetching submission: {e}")
        return None
