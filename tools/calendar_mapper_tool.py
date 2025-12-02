"""
Calendar Mapper tool - ADK version.
Maps available time slots for student scheduling.
"""
from typing import List, Optional
import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from core.db import get_user
from core.observability import logger

def get_available_time_slots(student_id: Optional[str] = None) -> List[str]:
    """
    Get available time slots for a student's schedule from Google Calendar.
    Calculates real free 30-minute slots between 4 PM and 9 PM.
    
    Args:
        student_id: The student's ID (email)
        
    Returns:
        List of available time slots (e.g. ["4:00 PM - 4:30 PM"])
    """
    if not student_id:
        return []

    user = get_user(student_id)
    if not user or 'tokens' not in user:
        logger.warning(f"No tokens found for user {student_id}")
        return []

    try:
        creds_data = user['tokens']
        creds = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri'),
            client_id=creds_data.get('client_id'),
            client_secret=creds_data.get('client_secret'),
            scopes=creds_data.get('scopes')
        )

        service = build('calendar', 'v3', credentials=creds)

        # Time range: Now to End of Day
        now = datetime.datetime.now()
        
        # Define Study Window: 4 PM to 9 PM today
        study_start = now.replace(hour=16, minute=0, second=0, microsecond=0)
        study_end = now.replace(hour=21, minute=0, second=0, microsecond=0)
        
        # If it's already past 9 PM, no slots today
        if now > study_end:
            return []
            
        # If it's past 4 PM, start from next 30-min chunk
        if now > study_start:
            # Round up to next 30 min
            delta_min = 30 - (now.minute % 30)
            if delta_min == 30: delta_min = 0
            study_start = now + datetime.timedelta(minutes=delta_min)
            study_start = study_start.replace(second=0, microsecond=0)

        # Fetch events for today
        # We fetch whole day to be safe, then filter
        day_start = now.replace(hour=0, minute=0, second=0)
        day_end = now.replace(hour=23, minute=59, second=59)
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=day_start.isoformat() + 'Z',
            timeMax=day_end.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        logger.info(f"Found {len(events)} calendar events for {student_id}")

        # Generate candidate 30-min slots
        available_slots = []
        current_slot = study_start
        
        while current_slot + datetime.timedelta(minutes=30) <= study_end:
            slot_end = current_slot + datetime.timedelta(minutes=30)
            is_conflict = False
            
            # Check for conflicts with existing events
            for event in events:
                # Parse event times (handling full day events which have 'date' instead of 'dateTime')
                start_str = event['start'].get('dateTime') or event['start'].get('date')
                end_str = event['end'].get('dateTime') or event['end'].get('date')
                
                try:
                    # Skip if parsing fails
                    pass 
                except:
                    continue

                # Check transparency: 'transparent' means the user is free (e.g. "Working elsewhere")
                if event.get('transparency') == 'transparent':
                    continue 
                
                # Check overlap logic
                if 'date' in event['start']:
                     # All day event - assume busy for the whole day
                     e_start = event['start']['date']
                     if e_start <= now.strftime('%Y-%m-%d'):
                         is_conflict = True
                         break
                elif 'dateTime' in event['start']:
                    # Time-based event
                    # We strip timezone offset for simple comparison (assuming local time consistency)
                    e_start_str = event['start']['dateTime'][:19] 
                    e_end_str = event['end']['dateTime'][:19]
                    
                    e_start_dt = datetime.datetime.fromisoformat(e_start_str)
                    e_end_dt = datetime.datetime.fromisoformat(e_end_str)
                    
                    # Overlap condition: (StartA < EndB) and (EndA > StartB)
                    if current_slot < e_end_dt and slot_end > e_start_dt:
                        is_conflict = True
                        break
            
            if not is_conflict:
                # Slot is free, add to list
                start_fmt = current_slot.strftime("%-I:%M %p")
                end_fmt = slot_end.strftime("%-I:%M %p")
                available_slots.append(f"{start_fmt} - {end_fmt}")
                
            current_slot = slot_end

        return available_slots

    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        return []

def get_calendar_events(student_id: Optional[str] = None) -> List[dict]:
    """
    Get raw calendar events for a student's schedule from Google Calendar.
    
    Args:
        student_id: The student's ID (email)
        
    Returns:
        List of calendar event objects
    """
    if not student_id:
        return []

    user = get_user(student_id)
    if not user or 'tokens' not in user:
        logger.warning(f"No tokens found for user {student_id}")
        return []

    try:
        creds_data = user['tokens']
        creds = Credentials(
            token=creds_data['token'],
            refresh_token=creds_data.get('refresh_token'),
            token_uri=creds_data.get('token_uri'),
            client_id=creds_data.get('client_id'),
            client_secret=creds_data.get('client_secret'),
            scopes=creds_data.get('scopes')
        )

        service = build('calendar', 'v3', credentials=creds)

        # Time range: Now to End of Day
        now = datetime.datetime.utcnow()
        end_of_day = now.replace(hour=23, minute=59, second=59)
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now.isoformat() + 'Z',
            timeMax=end_of_day.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])

    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        return []
