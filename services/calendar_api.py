import os
import json
import uuid
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = 'primary'

def get_calendar_service():
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
        # fallback для локальной разработки (если файл)
        SERVICE_ACCOUNT_FILE = 'credentials/service_account.json'
        if os.path.exists(SERVICE_ACCOUNT_FILE):
            creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        else:
            raise FileNotFoundError("Не найдены учётные данные Google Calendar")
    return build('calendar', 'v3', credentials=creds)

async def create_meeting(client_name: str, start_time_iso: str, duration_minutes: int = 30):
    service = get_calendar_service()
    start_time = datetime.fromisoformat(start_time_iso)
    end_time = start_time + timedelta(minutes=duration_minutes)
    
    event = {
        'summary': f'Созвон с клиентом {client_name}',
        'description': (
            'Обсуждение разработки AI-чат-бота.\n'
            'Ссылка для созвона будет отправлена перед встречей (Telegram, Zoom или Яндекс Телемост).\n'
            'Если вам удобнее другой сервис — сообщите.'
        ),
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/Moscow',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/Moscow',
        },
        'attendees': [],  # можно добавить email клиента, если он известен
    }
    
    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    event_link = created_event.get('htmlLink')
    meet_link = "🔗 Ссылка на созвон будет отправлена отдельным сообщением (выберите удобный сервис: Telegram, Zoom, Яндекс Телемост)"
    return meet_link, event_link
