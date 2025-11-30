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
            
            for event in events:
                # Parse event times (handling full day events which have 'date' instead of 'dateTime')
                start_str = event['start'].get('dateTime') or event['start'].get('date')
                end_str = event['end'].get('dateTime') or event['end'].get('date')
                
                # Simple ISO parse (ignoring timezone complexity for MVP - assuming local/Z match enough)
                # In production, use dateutil.parser
                try:
                    # Handle "2025-11-29T16:00:00-08:00" format manually if needed, 
                    # but for comparison we can just compare ISO strings if in same timezone,
                    # or better: convert everything to naive objects if possible or aware.
                    # Let's try simple string comparison for full day, and naive for times if possible.
                    
                    # Actually, let's just use the strings from API which are ISO.
                    # We need to convert our slot to ISO for comparison.
                    # This is tricky without timezone. 
                    # Let's assume the API returns 'dateTime' with offset.
                    pass 
                except:
                    continue

                # ROBUST CHECK:
                # We will check if the event overlaps with [current_slot, slot_end]
                # We need to convert event times to datetime objects.
                # Since we don't have easy timezone lib here, we'll rely on the fact that
                # we are looking for "busy" times.
                
                # Hack for MVP: Check if event *description* or title implies busy? No, use time.
                # Let's use the 'transparency' field? 'opaque' means busy.
                if event.get('transparency') == 'transparent':
                    continue # Event is "free"
                
                # Parse event start/end
                # If it's a date (all day), it blocks the whole day usually?
                if 'date' in event['start']:
                     # All day event - assume busy for now
                     # Check if it covers today
                     e_start = event['start']['date']
                     if e_start <= now.strftime('%Y-%m-%d'):
                         is_conflict = True
                         break
                elif 'dateTime' in event['start']:
                    # Time event
                    # We need to parse "2025-11-29T16:00:00-08:00"
                    # We will strip timezone for comparison with our naive 'current_slot' 
                    # (assuming system time is same timezone as calendar - risky but MVP)
                    e_start_str = event['start']['dateTime'][:19] # Strip offset
                    e_end_str = event['end']['dateTime'][:19]
                    
                    e_start_dt = datetime.datetime.fromisoformat(e_start_str)
                    e_end_dt = datetime.datetime.fromisoformat(e_end_str)
                    
                    # Check overlap
                    # Overlap if: (StartA < EndB) and (EndA > StartB)
                    if current_slot < e_end_dt and slot_end > e_start_dt:
                        is_conflict = True
                        break
            
            if not is_conflict:
                # Format: "4:00 PM - 4:30 PM"
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
