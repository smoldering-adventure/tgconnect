import signal
import sys
from telethon import TelegramClient, events  # type: ignore
from telethon.tl import types  # type: ignore
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
users_to_track = ['5239948967']  # Замените на реальные username или ID

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

    # Проверяем, что user не равен None
    if user is None:
        return

    # Проверяем, является ли пользователь одним из тех, кого мы отслеживаем
    if user.username in users_to_track or str(user.id) in users_to_track:
        current_status = user.status
        now = datetime.now()

        # Получаем последний известный статус пользователя
        last_seen = last_seen_status.get(user.username or str(user.id))

        # Если пользователь онлайн
        if isinstance(current_status, types.UserStatusOnline):
            if last_seen is None or not isinstance(last_seen, types.UserStatusOnline):
                print(f"{user.username or user.id} вошел в сеть: {now}")
                last_seen_status[user.username or str(user.id)] = current_status
                # Отправляем уведомление в Telegram
                send_telegram_message(f"{user.username or user.id} вошел в сеть в {now}")

        # Если пользователь вышел из сети
        elif isinstance(current_status, types.UserStatusOffline):
            if last_seen is not None and isinstance(last_seen, types.UserStatusOnline):
                print(f"{user.username or user.id} вышел из сети: {now}")
                last_seen_status[user.username or str(user.id)] = current_status
                # Отправляем уведомление в Telegram
                send_telegram_message(f"{user.username or user.id} вышел из сети в {now}")

async def main():
    await client.start(phone_number)
    print("Скрипт запущен. Ожидание изменений статуса...")
    await client.run_until_disconnected()

async def shutdown(signal, loop):
    """Корректное завершение работы."""
    print("\nЗавершение работы...")
    await client.disconnect()
    # Отменяем все задачи
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    # Ожидаем завершения всех задач
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    # Регистрируем обработчики сигналов
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig,
            lambda sig=sig: asyncio.create_task(shutdown(sig, loop))
        )

    try:
        # Запускаем клиент
        with client:
            loop.run_until_complete(main())
    except asyncio.CancelledError:
        # Игнорируем ошибку отмены задач
        pass
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        loop.close()