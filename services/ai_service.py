import os
import uuid
import base64
import logging
import httpx
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class GigaChatAsync:
    def __init__(self, base64_creds: str = None, model: str = "GigaChat"):
        self.base64_creds = base64_creds or os.getenv("GIGACHAT_BASE64")
        self.model = model
        self.access_token = None
        self.token_expires_at = None
        self.oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.chat_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    async def _get_token(self) -> str:
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.base64_creds}"
        }
        data = {"scope": "GIGACHAT_API_PERS"}
        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            resp = await client.post(self.oauth_url, headers=headers, data=data)
            if resp.status_code != 200:
                logger.error(f"Token error: {resp.status_code} - {resp.text}")
                raise Exception("Token error")
            tok = resp.json()
            self.access_token = tok["access_token"]
            expires_in = tok.get("expires_in", 1800)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            logger.info("Access token refreshed")
            return self.access_token

    async def chat(self, user_message: str) -> str:
        token = await self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        messages = [
            {"role": "system", "content": "Ты — AI-консультант по разработке чат-ботов. Отвечай кратко, дружелюбно, предлагай /price и /portfolio."},
            {"role": "user", "content": user_message}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            resp = await client.post(self.chat_url, headers=headers, json=payload)
            if resp.status_code != 200:
                logger.error(f"Chat error: {resp.status_code} - {resp.text}")
                raise Exception("Chat error")
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_with_system(self, user_message: str, system_prompt: str) -> str:
        token = await self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 300
        }
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            resp = await client.post(self.chat_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def chat_with_system_messages(self, messages: list) -> str:
        """
        Принимает готовый список сообщений с ролями (system, user, assistant)
        """
        token = await self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        async with httpx.AsyncClient(verify=False, timeout=60) as client:
            resp = await client.post(self.chat_url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
