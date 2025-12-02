import os
from google_auth_oauthlib.flow import Flow
from core.observability import logger

# Allow OAuth scope to change (e.g. if user grants fewer scopes or order changes)
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Scopes required for Google Classroom
SCOPES = [
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def get_flow(redirect_uri: str):
    """
    Create OAuth flow instance from client secrets.
    
    Args:
        redirect_uri: The URI to redirect to after Google login (must match Console).
        
    Returns:
        Flow object or None if credentials missing.
    """
    creds_path = os.getenv("GOOGLE_CLASSROOM_CREDENTIALS", "credentials.json")
    if not os.path.exists(creds_path):
        logger.error(f"Credentials file not found at {creds_path}")
        return None
        
    try:
        flow = Flow.from_client_secrets_file(
            creds_path,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        return flow
    except Exception as e:
        logger.error(f"Error creating OAuth flow: {e}")
        return None

def get_auth_url(redirect_uri: str, login_hint: str = None, state: str = None):
    """
    Generate the Google authentication URL for the user to visit.
    
    Args:
        redirect_uri: Callback URL
        login_hint: Email to pre-fill (optional)
        state: State string to prevent CSRF (optional)
        
    Returns:
        Tuple of (authorization_url, state)
    """
    flow = get_flow(redirect_uri)
    if not flow:
        return None
    
    # 'offline' access_type is required to get a refresh token
    kwargs = {
        'access_type': 'offline',
        'include_granted_scopes': 'true',
        'prompt': 'consent select_account'
    }
    if login_hint:
        kwargs['login_hint'] = login_hint
    
    if state:
        kwargs['state'] = state

    authorization_url, state = flow.authorization_url(**kwargs)
    return authorization_url, state

def exchange_code(code: str, redirect_uri: str):
    """Exchange auth code for credentials."""
    flow = get_flow(redirect_uri)
    if not flow:
        return None
        
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        return {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
    except Exception as e:
        logger.error(f"Error exchanging code: {e}")
        return None
