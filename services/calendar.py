import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'keys.json'  # можно загрузить из переменной окружения

def get_calendar_service():
    creds = None
    # Если ключ хранится в переменной окружения GOOGLE_CALENDAR_CREDS
    if os.getenv("GOOGLE_CALENDAR_CREDS"):
        creds_dict = json.loads(os.getenv("GOOGLE_CALENDAR_CREDS"))
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

async def create_meeting(client_email: str, client_name: str, start_time: datetime, duration_minutes=30):
    service = get_calendar_service()
    end_time = start_time + timedelta(minutes=duration_minutes)
    event = {
        'summary': f'Созвон с клиентом {client_name}',
        'description': 'Обсуждение разработки AI-чат-бота',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Europe/Moscow'},
        'attendees': [{'email': client_email}],
        'conferenceData': {
            'createRequest': {'requestId': f'req_{client_name}'}
        }
    }
    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    return event.get('hangoutLink'), event.get('htmlLink')