from tools.google_classroom_tool import list_assignments_for_student
import json

email = "nakshatra.bonda@gmail.com"
print(f"Fetching assignments for {email}...")
assignments = list_assignments_for_student(email)
print(f"Found {len(assignments)} assignments.")
print(json.dumps(assignments, indent=2))
