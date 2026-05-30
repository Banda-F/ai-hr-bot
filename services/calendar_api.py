import os
import json
import logging
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'primary'

def get_calendar_service():
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDS")
    if not creds_json:
        raise ValueError("GOOGLE_CALENDAR_CREDS not set")
    try:
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        return build('calendar', 'v3', credentials=creds)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in GOOGLE_CALENDAR_CREDS: {e}")
        raise
    except Exception as e:
        logger.error(f"Calendar service error: {e}")
        raise

async def create_meeting(client_name: str, start_time_iso: str, duration_minutes: int = 30):
    try:
        service = get_calendar_service()
        start_time = datetime.fromisoformat(start_time_iso)
        end_time = start_time + timedelta(minutes=duration_minutes)
        event = {
            'summary': f'Созвон с клиентом {client_name}',
            'description': 'Обсуждение разработки AI-чат-бота',
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Europe/Moscow'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Europe/Moscow'},
            'conferenceData': {
                'createRequest': {
                    'requestId': f'req_{client_name}_{int(start_time.timestamp())}',
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                }
            },
        }
        created_event = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event,
            conferenceDataVersion=1
        ).execute()
        meet_link = created_event.get('hangoutLink')
        event_link = created_event.get('htmlLink')
        return meet_link, event_link
    except Exception as e:
        logger.error(f"Ошибка создания встречи: {e}")
        raise
