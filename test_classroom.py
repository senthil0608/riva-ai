#!/usr/bin/env python3
"""
Test script for Google Classroom integration.
This script tests the classroom_sync_agent with a real Google Classroom account.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.classroom_sync_agent import run_classroom_sync
from tools.google_classroom_tool import get_classroom_service, list_assignments_for_student

def test_authentication():
    """Test Google Classroom authentication."""
    print("=" * 60)
    print("STEP 1: Testing Google Classroom Authentication")
    print("=" * 60)
    
    service = get_classroom_service()
    
    if service:
        print("✅ Successfully authenticated with Google Classroom!")
        return True
    else:
        print("❌ Authentication failed.")
        print("\nPlease ensure:")
        print("1. You have created credentials.json from Google Cloud Console")
        print("2. Google Classroom API is enabled")
        print("3. credentials.json is in the project root directory")
        return False


def test_list_courses(student_email):
    """Test listing courses for a student."""
    print("\n" + "=" * 60)
    print("STEP 2: Testing Course Listing")
    print("=" * 60)
    
    service = get_classroom_service()
    if not service:
        print("❌ Cannot test without authentication")
        return False
    
    try:
        print(f"\nFetching courses for: {student_email}")
        courses_result = service.courses().list(
            studentId=student_email,
            courseStates=['ACTIVE']
        ).execute()
        
        courses = courses_result.get('courses', [])
        
        if not courses:
            print(f"⚠️  No active courses found for {student_email}")
            print("\nPossible reasons:")
            print("1. The email doesn't have access to any Google Classroom courses")
            print("2. The email is not enrolled as a student")
            print("3. All courses are archived or deleted")
            return False
        
        print(f"\n✅ Found {len(courses)} active course(s):")
        for i, course in enumerate(courses, 1):
            print(f"   {i}. {course['name']} (ID: {course['id']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing courses: {e}")
        return False


def test_list_assignments(student_email):
    """Test listing assignments using the tool."""
    print("\n" + "=" * 60)
    print("STEP 3: Testing Assignment Listing")
    print("=" * 60)
    
    try:
        print(f"\nFetching assignments for: {student_email}")
        assignments = list_assignments_for_student(student_email)
        
        if not assignments:
            print("⚠️  No assignments found")
            return False
        
        print(f"\n✅ Found {len(assignments)} assignment(s):")
        for i, assignment in enumerate(assignments, 1):
            print(f"\n   {i}. {assignment['title']}")
            print(f"      Subject: {assignment['subject']}")
            print(f"      Due: {assignment['due']}")
            print(f"      ID: {assignment['id']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error listing assignments: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_classroom_sync_agent(student_email):
    """Test the classroom_sync_agent."""
    print("\n" + "=" * 60)
    print("STEP 4: Testing classroom_sync_agent")
    print("=" * 60)
    
    try:
        print(f"\nRunning classroom_sync_agent for: {student_email}")
        result = run_classroom_sync(student_email)
        
        assignments = result.get('assignments', [])
        
        if not assignments:
            print("⚠️  Agent returned no assignments")
            return False
        
        print(f"\n✅ Agent successfully retrieved {len(assignments)} assignment(s):")
        for i, assignment in enumerate(assignments, 1):
            print(f"   {i}. {assignment['title']} ({assignment['subject']}) - Due: {assignment['due']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function."""
    print("\n" + "=" * 60)
    print("Google Classroom Integration Test")
    print("=" * 60)
    
    # Get student email from command line or use default
    if len(sys.argv) > 1:
        student_email = sys.argv[1]
    else:
        student_email = input("\nEnter student email address (or press Enter to use 'me'): ").strip()
        if not student_email:
            student_email = "me"  # 'me' refers to the authenticated user
    
    print(f"\nTesting with student: {student_email}")
    
    # Run tests
    results = []
    
    # Test 1: Authentication
    results.append(("Authentication", test_authentication()))
    
    if not results[0][1]:
        print("\n" + "=" * 60)
        print("SETUP REQUIRED")
        print("=" * 60)
        print("\nTo set up Google Classroom integration:")
        print("\n1. Go to: https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Classroom API")
        print("4. Create OAuth 2.0 credentials (Desktop app)")
        print("5. Download credentials.json to project root")
        print("\nFor detailed instructions, see: GOOGLE_CLASSROOM.md")
        return
    
    # Test 2: List courses
    results.append(("List Courses", test_list_courses(student_email)))
    
    # Test 3: List assignments
    results.append(("List Assignments", test_list_assignments(student_email)))
    
    # Test 4: classroom_sync_agent
    results.append(("classroom_sync_agent", test_classroom_sync_agent(student_email)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Google Classroom integration is working.")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")


if __name__ == "__main__":
    main()
