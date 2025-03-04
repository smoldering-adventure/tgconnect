from telethon import TelegramClient, events  # type: ignore
from telethon.tl.types import UserStatusOnline, UserStatusOffline  # type: ignore
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import asyncio

# Ваши данные API Telegram
api_id = '28959681'
api_hash = 'de1a5bdef4d5c7b9a2f6138219fb7b3f'
phone_number = '79522480324'

# Данные для отправки почты через Gmail
gmail_user = 'm.p.w.200032@gmail.com'  # Ваш Gmail
gmail_password = '32022010'  # Пароль от Gmail или пароль приложения
to_email = 'm.p.w.200032@gmail.com'  # Почта, на которую будут отправляться уведомления

# Список пользователей для отслеживания (username или ID)
users_to_track = ['5239948967', '5159723893']  # Замените на реальные username или ID

# Создаем клиент Telegram
client = TelegramClient('session_name', api_id, api_hash)

# Словарь для хранения последнего известного статуса каждого пользователя
last_seen_status = {user: None for user in users_to_track}

# Функция для отправки email
def send_email(subject, body):
    try:
        # Создаем сообщение
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = gmail_user
        msg['To'] = to_email

        # Отправляем сообщение через SMTP-сервер Gmail
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())
        print("Уведомление отправлено на почту.")
    except Exception as e:
        print(f"Ошибка при отправке email: {e}")

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
        if isinstance(current_status, UserStatusOnline):
            if last_seen is None or not isinstance(last_seen, UserStatusOnline):
                print(f"{user.username or user.id} вошел в сеть: {now}")
                last_seen_status[user.username or str(user.id)] = current_status
                # Отправляем уведомление на почту
                send_email(
                    f"Telegram: {user.username or user.id} вошел в сеть",
                    f"{user.username or user.id} вошел в сеть в {now}"
                )

        # Если пользователь вышел из сети
        elif isinstance(current_status, UserStatusOffline):
            if last_seen is not None and isinstance(last_seen, UserStatusOnline):
                print(f"{user.username or user.id} вышел из сети: {now}")
                last_seen_status[user.username or str(user.id)] = current_status
                # Отправляем уведомление на почту
                send_email(
                    f"Telegram: {user.username or user.id} вышел из сети",
                    f"{user.username or user.id} вышел из сети в {now}"
                )

async def main():
    await client.start(phone_number)
    print("Скрипт запущен. Ожидание изменений статуса...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())