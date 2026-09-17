import asyncio

from celery_app.celery import celery
import core.database.requests as rq
import requests

from core.settings import settings
import core.handlers.texts as txt

from celery_app.analysis import analysis

import nest_asyncio


BOT_TOKEN = settings.BOT_TOKEN


def send_notif(ids: list[int], kp: int):
    loop = asyncio.get_event_loop()
    if loop.is_running():
        nest_asyncio.apply()
    if not BOT_TOKEN:
        print("⚠️ Telegram bot token или chat ID не заданы")
        return
    if kp < 4:
        desc = (
            f"Сегодня максимальный Kp-индекс будет <b>{kp}</b> — спокойная геомагнитная обстановка.\n\n"
            "🔹 <b>Самочувствие:</b> большинство людей чувствуют себя хорошо. Редко отмечаются жалобы.\n"
            "Узнать больше можно по кнопке '📊 Прогноз на сегодня'."
        )
    elif kp < 5:
        desc = (
            f"Сегодня максимальный Kp-индекс будет <b>{kp}</b> — неустойчивая геомагнитная обстановка.\n\n"
            "🔸 <b>Самочувствие:</b> возможны лёгкие недомогания у метеочувствительных людей: головная боль, усталость, перепады настроения.\n"
            "Узнать больше можно по кнопке '📊 Прогноз на сегодня'."
        )
    elif kp < 6:
        desc = (
            f"Сегодня максимальный Kp-индекс будет <b>{kp}</b> — слабая геомагнитная буря.\n\n"
            "⚠️ <b>Самочувствие:</b> у метеозависимых — повышенная утомляемость, головокружение, скачки давления. Рекомендуется избегать стрессов и физических нагрузок.\n"
            "Узнать больше можно по кнопке '📊 Прогноз на сегодня'."
        )
    elif kp < 7:
        desc = (
            f"Сегодня максимальный Kp-индекс будет <b>{kp}</b> — умеренная геомагнитная буря.\n\n"
            "❗ <b>Самочувствие:</b> значительное ухудшение самочувствия у чувствительных людей. Возможны боли в суставах, сердцебиение, нарушение сна. Следите за состоянием здоровья.\n"
            "Узнать больше можно по кнопке '📊 Прогноз на сегодня'."
        )
    elif kp < 8:
        desc = (
            f"Сегодня максимальный Kp-индекс будет <b>{kp}</b> — сильная геомагнитная буря.\n\n"
            "❗❗ <b>Самочувствие:</b> высокий риск ухудшения: головные боли, давление, сердечные приступы у предрасположенных. Рекомендуется придерживаться режима, избегать алкоголя и кофе.\n"
            "Узнать больше можно по кнопке '📊 Прогноз на сегодня'."
        )
    elif kp < 9:
        desc = (
            f"Сегодня максимальный Kp-индекс будет <b>{kp}</b> — очень сильная геомагнитная буря.\n\n"
            "❌ <b>Самочувствие:</b> возможны серьёзные симптомы даже у здоровых людей. Людям с хроническими заболеваниями — особенно осторожно. Обратите внимание на своё состояние.\n"
            "Узнать больше можно по кнопке '📊 Прогноз на сегодня'."
        )
    else:
        desc = (
            f"Сегодня максимальный Kp-индекс будет <b>{kp}</b> — экстремальная геомагнитная буря.\n\n"
            "🆘 <b>Самочувствие:</b> высокий риск серьёзных нарушений самочувствия. Возможны обострения хронических заболеваний, скачки давления, головокружение. Следите за здоровьем, при необходимости — обратитесь к врачу.\n"
            "Узнать больше можно по кнопке '📊 Прогноз на сегодня'."
        )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for user_id in ids:
        last = loop.run_until_complete(rq.get_last_health_by_kp_for_user(user_id, kp))
        if last is not None:
            health = loop.run_until_complete(analysis(last))
        else:
            health = None
        payload = {
            "chat_id": user_id,
            "text": desc + (health or ""),
            "parse_mode": "HTML",
            "reply_markup":  {
                "inline_keyboard": [
                        [
                            {
                                "text": "😣 плохо",
                                "callback_data": "query bad",
                                "style": "danger"
                            }
                        ],
                        [
                            {
                                "text": "😑 приемлемо",
                                "callback_data": "query normal",
                                "style": "primary"
                            }
                        ],
                        [
                            {
                                "text": "😀 хорошо",
                                "callback_data": "query good",
                                "style": "success"
                            }
                        ]
                    ]
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
            "text": f"❓Оцените ваше самочувствие",
            "parse_mode": "Markdown",
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "😣 плохо", "callback_data": "query bad"},
                    ],
                    [
                        {"text": "😑 приемлемо", "callback_data": "query normal"},
                    ],
                    [
                        {"text": "😀 хорошо", "callback_data": "query good"},
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

        kp = loop.run_until_complete(txt.get_kp_forecast_report(only_max=True))

        users_ids = loop.run_until_complete(rq.get_user_ids_for_kp(kp))

        send_notif(users_ids, kp)
    except Exception as e:
        error_msg = f"{type(e).__name__}: {e}"
        print(f"❌ Ошибка: {error_msg}")




@celery.task
def query_user():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        nest_asyncio.apply()
    ids = loop.run_until_complete(rq.get_user_ids_for_query())
    send_query(ids)
