import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from core.observability import logger

# Initialize Firebase
# We check if the app is already initialized to avoid errors during hot-reloads or multiple imports.
try:
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        else:
            logger.warning(f"Firebase credentials not found at {cred_path}")
except Exception as e:
    logger.error(f"Error initializing Firebase: {e}")

def get_db():
    """Get Firestore client."""
    try:
        return firestore.client()
    except Exception as e:
        logger.error(f"Error getting Firestore client: {e}")
        return None

def save_user(email: str, data: dict):
    """
    Save or update user data in Firestore.
    
    Uses 'merge=True' to ensure we don't overwrite existing fields (like 'student_emails')
    when just updating status or cache.
    
    Args:
        email: The user's email (used as Document ID).
        data: The dictionary of fields to update.
    """
    db = get_db()
    if not db:
        return False
    try:
        db.collection("users").document(email).set(data, merge=True)
        return True
    except Exception as e:
        logger.error(f"Error saving user {email}: {e}")
        return False

def get_user(email: str):
    """Get user data from Firestore."""
    db = get_db()
    if not db:
        return None
    try:
        doc = db.collection("users").document(email).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error(f"Error getting user {email}: {e}")
        return None

def find_user_by_email(email: str):
    """
    Find a user document that contains the given email in student_emails or parent_emails.
    """
    db = get_db()
    if not db:
        return None
    try:
        # 1. Try direct lookup (fastest)
        doc = db.collection("users").document(email).get()
        if doc.exists:
            return doc.to_dict()
            
        # 2. Query student_emails
        students = db.collection("users").where("student_emails", "array_contains", email).limit(1).stream()
        for user in students:
            return user.to_dict()
            
        # 3. Query parent_emails
        parents = db.collection("users").where("parent_emails", "array_contains", email).limit(1).stream()
        for user in parents:
            return user.to_dict()
            
        return None
    except Exception as e:
        logger.error(f"Error finding user by email {email}: {e}")
        return None

def get_active_student(email: str = None):
    """
    Get the active student from Firestore.
    If email is provided, fetches the user associated with that email.
    If not, falls back to the first user (legacy behavior).
    """
    if email:
        return find_user_by_email(email)

    db = get_db()
    if not db:
        return None
    try:
        # For now, just get the first user found. 
        # In a real multi-tenant app, we'd need session context.
        users = db.collection("users").limit(1).stream()
        for user in users:
            return user.to_dict()
        return None
    except Exception as e:
        logger.error(f"Error getting active student: {e}")
        return None
