from telethon import TelegramClient, events  # type: ignore
from datetime import datetime
import requests  # type: ignore
import asyncio

# Ваши данные API Telegram
api_id = '28959681'  # Замените на ваш API ID
api_hash = 'de1a5bdef4d5c7b9a2f6138219fb7b3f'  # Замените на ваш API Hash
phone_number = '79522480324'  # Ваш номер телефона

# Токен вашего бота и chat_id
BOT_TOKEN = '7682182486:AAFLLXRZoN1tPu0taAPNqga31q_Eq6GDWpI'  # Замените на токен вашего бота
CHAT_ID = '5159723893'  # Замените на ваш chat_id

# Список пользователей для отслеживания (username или ID)
users_to_track = ['5239948967', '5159723893']  # Замените на реальные username или ID

# Создаем клиент Telegram
client = TelegramClient('session_name', api_id, api_hash)

# Словарь для хранения последнего известного статуса каждого пользователя
last_seen_status = {user: None for user in users_to_track}

def send_telegram_message(message):
    """Отправляет сообщение в Telegram."""
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHAT_ID,
        'text': message,
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Уведомление отправлено в Telegram.")
        else:
            print(f"Ошибка при отправке сообщения: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

@client.on(events.UserUpdate)
async def handler(event):
    user = await event.get_sender()

    # Проверяем, является ли пользователь одним из тех, кого мы отслеживаем
    if user.username in users_to_track or str(user.id) in users_to_track:
        current_status = user.status
        now = datetime.now()

        # Получаем последний известный статус пользователя
        last_seen = last_seen_status.get(user.username or str(user.id))

        # Если пользователь онлайн
        if isinstance(current_status, telethon.tl.types.UserStatusOnline):  # type: ignore
            if last_seen is None or not isinstance(last_seen, telethon.tl.types.UserStatusOnline):  # type: ignore
                print(f"{user.username or user.id} вошел в сеть: {now}")
                last_seen_status[user.username or str(user.id)] = current_status
                # Отправляем уведомление в Telegram
                send_telegram_message(f"{user.username or user.id} вошел в сеть в {now}")

        # Если пользователь вышел из сети
        elif isinstance(current_status, telethon.tl.types.UserStatusOffline):  # type: ignore
            if last_seen is not None and isinstance(last_seen, telethon.tl.types.UserStatusOnline):  # type: ignore
                print(f"{user.username or user.id} вышел из сети: {now}")
                last_seen_status[user.username or str(user.id)] = current_status
                # Отправляем уведомление в Telegram
                send_telegram_message(f"{user.username or user.id} вышел из сети в {now}")

async def main():
    await client.start(phone_number)
    print("Скрипт запущен. Ожидание изменений статуса...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())