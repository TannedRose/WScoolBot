import asyncio

from celery_app.celery import celery
import core.database.requests as rq
import requests

from core.settings import settings
import core.handlers.texts as txt

import nest_asyncio


BOT_TOKEN = settings.BOT_TOKEN

def send_notif(ids: list):
    if not BOT_TOKEN:
        print("⚠️ Telegram bot token или chat ID не заданы")
        return
    loop = asyncio.get_event_loop()
    if loop.is_running():
        nest_asyncio.apply()
    kp = loop.run_until_complete(txt.get_kp_forecast_report(only_max=True))
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for user_id in ids:
        payload = {
            "chat_id": user_id,
            "text": f"Сегодня максимальный Кр индекс будет <b>{kp}</b>, узнать больше можно по кнопке 'прогноз на сегодня'",
            "parse_mode": "HTML",
            "reply_markup":  {
                "inline_keyboard": [
                    [
                        {"text": "Настройки", "callback_data": "settings"},
                    ],
                    [
                        {"text": "Прогноз на завтра", "callback_data": "predict_weather"}
                    ],
                    [
                        {"text": "Прогноз на сегодня", "callback_data": "now_weather"}
                    ]
                ]
            }
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as ex:
            print(f"❌ Не удалось отправить в TG: {ex}")


def send_query(ids: list):
    if not BOT_TOKEN :
        print("⚠️ Telegram bot token или chat ID не заданы")
        return
    print("TRY")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for i in ids:
        payload = {
            "chat_id": i,
            "text": f"Как вы чувствовали себя сегодня?",
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "Все хорошо", "callback_data": "query all_good"},
                        {"text": "Слабость", "callback_data": "query weakness"}
                    ],
                    [
                        {"text": "Головные боли", "callback_data": "query head_pain"}
                    ]
                ]
            }
        }
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception as ex:
            print(f"❌ Не удалось отправить в TG: {ex}")

@celery.task
def send_notification():
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            nest_asyncio.apply()
        users_ids = loop.run_until_complete(rq.get_user_ids(for_notifications=True))
        send_notif(users_ids)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        print(f"❌ Ошибка: {error_msg}")



@celery.task
def query_user():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        nest_asyncio.apply()
    ids = loop.run_until_complete(rq.get_user_ids(for_qwery=True))
    send_query(ids)
