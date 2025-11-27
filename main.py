"""
Simple demo script for Riva AI - ADK version.
"""
from agents import run_aura_orchestrator
from core.config import STUDENT_EMAILS


def main():
    """Run a simple demo of the Aura orchestrator."""
    print("=" * 60)
    print("Riva AI - Academic Coach Demo")
    print("=" * 60)
    print()
    
    student_id = STUDENT_EMAILS[0]
    print(f"Running Aura orchestrator for student: {student_id}")
    print()
    
    # Run orchestrator
    result = run_aura_orchestrator(student_id)
    
    # Display results
    print()
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print()
    
    print(f"📚 Assignments: {len(result['assignments'])}")
    for assignment in result['assignments']:
        print(f"  - {assignment['title']} ({assignment['subject']}) - Due: {assignment['due']}")
    
    print()
    print("📊 Skill Profile:")
    for subject, level in result['skill_profile'].items():
        print(f"  - {subject}: {level}")
    
    print()
    print(f"📅 Daily Plan: {len(result['daily_plan'])} tasks")
    for task in result['daily_plan']:
        print(f"  - {task['time']}: {task['title']} ({task['subject']}) [{task['difficulty_tag']}]")
    
    print()
    print("👨‍👩‍👧 Parent Summary:")
    print(f"  {result['parent_summary']['summary_text']}")
    print(f"  Stress Level: {result['parent_summary']['stress_level']}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
