import asyncio
from services.calendar_api import create_meeting

async def test():
    meet_link, event_link = await create_meeting("Тест", "2025-06-01T12:00:00")
    print("Meet:", meet_link)
    print("Event:", event_link)

asyncio.run(test())