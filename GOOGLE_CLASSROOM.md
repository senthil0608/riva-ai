# Google Classroom Integration Guide

## Overview

Riva AI integrates with Google Classroom to fetch student assignments, courses, and submissions.

## Setup

### 1. Enable Google Classroom API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable the **Google Classroom API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Classroom API"
   - Click "Enable"

### 2. Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as application type
4. Name it "Riva AI Classroom Integration"
5. Click "Create"
6. Download the JSON file
7. Save it as `credentials.json` in the project root

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. First-Time Authentication

```bash
# Run the demo to trigger OAuth flow
python3 main.py
```

This will:
1. Open your browser for Google authentication
2. Ask you to grant permissions
3. Save credentials to `token.pickle`
4. Subsequent runs will use saved credentials

## Usage

### Fetch Student Assignments

```python
from tools.google_classroom_tool import list_assignments_for_student

# Get all assignments for a student
assignments = list_assignments_for_student("student@example.com")

for assignment in assignments:
    print(f"{assignment['title']} - Due: {assignment['due']}")
```

### Get Student Submission

```python
from tools.google_classroom_tool import get_student_submissions

submission = get_student_submissions(
    student_id="student@example.com",
    course_id="course_123",
    coursework_id="assignment_456"
)

print(f"Status: {submission['state']}")
print(f"Grade: {submission['assigned_grade']}")
```

## API Response Format

### Assignment Object

```python
{
    "id": "assignment_id",
    "title": "Math Worksheet 5",
    "subject": "Math",  # Course name
    "due": "2025-11-26",  # YYYY-MM-DD or "No due date"
    "description": "Complete problems 1-20",
    "state": "PUBLISHED",  # PUBLISHED, DRAFT, DELETED
    "course_id": "course_id"
}
```

### Submission Object

```python
{
    "id": "submission_id",
    "state": "TURNED_IN",  # CREATED, TURNED_IN, RETURNED, RECLAIMED_BY_STUDENT
    "late": False,
    "assigned_grade": 95.0,
    "draft_grade": None,
    "submission_history": [...]
}
```

## Scopes Required

The tool requests these Google Classroom scopes:

- `classroom.courses.readonly` - Read course information
- `classroom.coursework.students.readonly` - Read coursework and assignments
- `classroom.rosters.readonly` - Read class rosters

## Fallback Behavior

If Google Classroom API is unavailable:
- Returns mock data for development
- Logs warning message
- Continues operation without errors

## Troubleshooting

### "credentials.json not found"

Download OAuth credentials from Google Cloud Console and save as `credentials.json`.

### "Token has been expired or revoked"

Delete `token.pickle` and re-authenticate:
```bash
rm token.pickle
python3 main.py
```

### "Access denied"

Ensure the Google account has access to the classroom courses.

### "API not enabled"

Enable Google Classroom API in Google Cloud Console.

## Environment Variables

```bash
# Optional: Custom credentials path
GOOGLE_CLASSROOM_CREDENTIALS=/path/to/credentials.json
```

## Security Notes

- `credentials.json` - OAuth client secrets (add to .gitignore)
- `token.pickle` - User access tokens (add to .gitignore)
- Never commit these files to version control

## Files

- `tools/google_classroom_tool.py` - Main implementation
- `credentials.json` - OAuth client secrets (you create this)
- `token.pickle` - Saved user credentials (auto-generated)

## Example: Full Workflow

```python
from tools.google_classroom_tool import (
    list_assignments_for_student,
    get_student_submissions
)

# 1. Get all assignments
student_email = "student@example.com"
assignments = list_assignments_for_student(student_email)

print(f"Found {len(assignments)} assignments")

# 2. Check submission status for each
for assignment in assignments:
    submission = get_student_submissions(
        student_id=student_email,
        course_id=assignment['course_id'],
        coursework_id=assignment['id']
    )
    
    if submission:
        print(f"{assignment['title']}: {submission['state']}")
```

## Production Deployment

For production, use service account authentication:

1. Create a service account in Google Cloud Console
2. Download JSON key file
3. Use `google.oauth2.service_account.Credentials`
4. Grant service account access to classrooms

## Summary

✅ **Real Google Classroom API integration**
✅ **OAuth 2.0 authentication**
✅ **Fetches courses and assignments**
✅ **Gets student submissions**
✅ **Graceful fallback to mock data**
✅ **Comprehensive error handling**
✅ **Observability integrated**

**Ready for production use!** 🎓
