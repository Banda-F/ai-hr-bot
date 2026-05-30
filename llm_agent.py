import os
import asyncio
from gigachat import GigaChat

# Получаем данные из переменных окружения (добавьте их в Render)
GIGACHAT_CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
GIGACHAT_MODEL = os.getenv("GIGACHAT_MODEL", "GigaChat-2")

# Функция для отправки запроса к GigaChat
async def generate_response(user_message: str, context: dict) -> str:
    if not GIGACHAT_CREDENTIALS:
        return "Нейросеть временно недоступна. Пожалуйста, свяжитесь с нами напрямую."

    try:
        # Важно: для асинхронной работы в aiogram нужно использовать sync_to_async
        from asyncio import to_thread
        from gigachat.models import Chat, Messages, MessagesRole

        # Извлекаем историю из контекста, если она была передана
        history = context.get('history', [])

        # Формируем сообщения для GigaChat
        messages = [
            {
                "role": "system",
                "content": "Ты полезный ассистент по подбору курьеров. Отвечай вежливо, кратко и по делу. Если тебя спрашивают о работе курьером, расскажи о преимуществах: доход от 4000₽ в день, гибкий график, поддержка наставников. Если не знаешь ответа, честно скажи об этом и предложи связаться с оператором. Держи тон дружественным и поддерживающим, задавай уточняющие вопросы. В своих ответах используй ⏱️, 📦, 🚀."
            }
        ]

        # Добавляем историю диалога (последние N сообщений)
        for msg in history[-10:]:
            messages.append(msg)

        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": user_message})

        # Выполняем API-вызов GigaChat
        with GigaChat(credentials=GIGACHAT_CREDENTIALS, model=GIGACHAT_MODEL, verify_ssl_certs=False) as giga:
            response = await to_thread(giga.chat, messages=messages)

        # Урезаем историю, чтобы не превышать лимит токенов
        updated_history = history + [{"role": "user", "content": user_message}, {"role": "assistant", "content": response.choices[0].message.content}]
        if len(updated_history) > 10:
            updated_history = updated_history[-10:]

        # Возвращаем ответ и обновлённую историю
        return response.choices[0].message.content, updated_history

    except Exception as e:
        # Логируем ошибку для отладки
        print(f"Ошибка GigaChat: {e}")
        return "Извините, произошла техническая ошибка. Попробуйте позже или напишите нашему менеджеру.", history