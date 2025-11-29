import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
user_ref = db.collection("users").document("nakshatra_bonda@myabcusd.org")

# Update with correct emails
user_ref.set({
    "student_emails": ["nakshatra_bonda@myabcusd.org", "nakshatra.bonda@gmail.com"],
    "parent_emails": ["suresh.bonda@gmail.com"] # Assuming this based on context
}, merge=True)

print("Updated user data.")

# Verify
doc = user_ref.get()
print(f"New Data: {doc.to_dict()}")
