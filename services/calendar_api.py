import os
import json
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# --- НАСТРОЙКИ ---
# Укажите ваш email (тот же, что использовали для расшаривания календаря)
CALENDAR_ID = 'eugen.myakotin@gmail.com'  # замените на ваш email
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds_json = os.getenv("GOOGLE_CALENDAR_CREDS")
    if creds_json:
        creds_dict = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    else:
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
            'Обсуждение разработки AI-чат-бота.\n\n'
            'Ссылка для созвона: Telegram, Zoom или Яндекс Телемост (уточните у администратора).'
        ),
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Europe/Moscow',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Europe/Moscow',
        },
        # Нет attendees и sendUpdates – избегаем ошибки 403
    }
    
    created_event = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event
    ).execute()
    
    event_link = created_event.get('htmlLink')
    meet_link = "🔗 Ссылка на созвон будет отправлена отдельным сообщением"
    return meet_link, event_link
