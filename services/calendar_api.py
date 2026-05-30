import os
import json
from datetime import datetime, timedelta

# Проверяем наличие библиотек Google
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Библиотеки Google не установлены. Функции календаря отключены.")

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'primary'

def get_calendar_service():
    if not GOOGLE_AVAILABLE:
        return None
    creds = None
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    elif os.path.exists("credentials/bot-curier-7a09e4a0127b.json"):
        creds = service_account.Credentials.from_service_account_file("credentials/bot-curier-7a09e4a0127b.json", scopes=SCOPES)
    else:
        return None
    return build('calendar', 'v3', credentials=creds)

async def create_meeting(client_name: str, start_time_iso: str, duration_minutes: int = 30):
    if not GOOGLE_AVAILABLE:
        return None, None
    service = get_calendar_service()
    if not service:
        return None, None
    start_time = datetime.fromisoformat(start_time_iso)
    end_time = start_time + timedelta(minutes=duration_minutes)
    event = {
        'summary': f'Созвон с клиентом {client_name}',
        'description': 'Обсуждение разработки AI-чат-бота',
        'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Europe/Moscow'},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Europe/Moscow'},
        'attendees': [],
        'conferenceData': {
            'createRequest': {'requestId': f'req_{client_name}_{start_time.timestamp()}'}
        }
    }
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event, conferenceDataVersion=1).execute()
    return created_event.get('hangoutLink'), created_event.get('htmlLink')