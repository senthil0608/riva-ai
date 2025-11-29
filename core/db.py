import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from core.observability import logger

# Initialize Firebase
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
    """Save or update user data in Firestore."""
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

def get_active_student():
    """
    Get the first configured student from Firestore.
    This replaces the old config.STUDENT_EMAILS logic.
    """
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
