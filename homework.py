import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BOT = telegram.Bot(token=TELEGRAM_TOKEN)


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    if homework_name is None:
        return 'Нет имени'
    homework_status = homework.get('status')
    if homework_status in ('approved', 'rejected'):
        if homework_status != 'approved':
            verdict = 'К сожалению в работе нашлись ошибки.'
        else:
            verdict = ('Ревьюеру всё понравилось, можно приступать '
                       'к следующему уроку.')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    else:
        return 'Статус не корректен'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    data = {'from_date': current_timestamp}
    homework_statuses = requests.get(
        'https://praktikum.yandex.ru/api/user_api/homework_statuses/',
        headers=headers, params=data
    )
    return homework_statuses.json()


def send_message(message):
    return BOT.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                last_homework = new_homework.get('homeworks')[0]
                send_message(parse_homework_status(last_homework))
            current_timestamp = new_homework.get(
                'current_date', int(time.time()))  # обновить timestamp
            time.sleep(900)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
