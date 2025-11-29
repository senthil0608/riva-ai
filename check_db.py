import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()
users = db.collection("users").stream()

print("--- Users in Firestore ---")
for user in users:
    data = user.to_dict()
    print(f"ID: {user.id}")
    print(f"Student Emails: {data.get('student_emails')}")
    print(f"Tokens Present: {'tokens' in data}")
    if 'tokens' in data:
        print(f"Token Scopes: {data['tokens'].get('scopes')}")
    print("----------------")
