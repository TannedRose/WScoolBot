import math

import aiohttp
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

start = """
🌌 Добро пожаловать!  
Вы в пространстве, где космос делится своими тайнами.
Здесь вы узнаете, когда солнечный ветер усиливается, а магнитные бури могут повлиять на самочувствие и настроение.

☀️ Я буду вашим проводником по небесным ритмам:
-расскажу о текущей активности Солнца,
-предупрежу о грядущих всплесках,
🔔 Подписывайтесь на прогнозы — и пусть космос больше не застает вас врасплох!
"""

setup = """
⚙️ Настройки

🔔 Уведомления — 08:00  
📅 Утром получите прогноз на день  
▸ Можно задать минимальный порог для уведомлений  

📝 Опрос — 20:00  
🌙 Вечером бот спросит о самочувствии
"""


main = """
✅ Вы в главном меню
"""


async def get_kp_forecast_report(days_ahead: int = 0, only_max: bool = False):
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"

    # --- загрузка данных ---
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
    except Exception as e:
        return f"❌ Ошибка загрузки данных: {e}"

    if not data or len(data) < 2:
        return "❌ Пустой ответ от NOAA."

    headers = data[0]

    # ---------------------------------------------------------
    # Определяем столбцы
    # ---------------------------------------------------------

    if isinstance(headers, list):
        time_col = next(
            (
                i for i, h in enumerate(headers)
                if isinstance(h, str) and "time" in h.lower()
            ),
            None
        )

        kp_col = next(
            (
                i for i, h in enumerate(headers)
                if isinstance(h, str) and "kp" in h.lower()
            ),
            None
        )

        obs_col = next(
            (
                i for i, h in enumerate(headers)
                if isinstance(h, str)
                and (
                    "obs" in h.lower()
                    or "forecast" in h.lower()
                    or "status" in h.lower()
                )
            ),
            None
        )

    elif isinstance(headers, dict):
        # На случай, если NOAA вернёт объект вместо списка заголовков
        keys = list(headers.keys())

        time_col = next(
            (
                key for key in keys
                if isinstance(key, str) and "time" in key.lower()
            ),
            None
        )

        kp_col = next(
            (
                key for key in keys
                if isinstance(key, str) and "kp" in key.lower()
            ),
            None
        )

        obs_col = next(
            (
                key for key in keys
                if isinstance(key, str)
                and (
                    "obs" in key.lower()
                    or "forecast" in key.lower()
                    or "status" in key.lower()
                )
            ),
            None
        )

    else:
        return "❌ Неизвестный формат данных NOAA."

    if time_col is None or kp_col is None:
        return f"❌ Не найдены нужные столбцы. Заголовки: {headers}"

    # ---------------------------------------------------------
    # Целевая дата
    # ---------------------------------------------------------

    target_date = (
        datetime.now(timezone.utc).date()
        + timedelta(days=days_ahead)
    )

    rows: List[Tuple[datetime, int, str]] = []

    # ---------------------------------------------------------
    # Обработка строк
    # ---------------------------------------------------------

    for row in data[1:]:

        # Если строка — список
        if isinstance(row, list):

            if not isinstance(time_col, int) or not isinstance(kp_col, int):
                continue

            if len(row) <= max(time_col, kp_col):
                continue

            time_str = row[time_col]
            kp_str = row[kp_col]

            if obs_col is not None and isinstance(obs_col, int):
                obs_type = (
                    str(row[obs_col]).lower()
                    if len(row) > obs_col and row[obs_col]
                    else ""
                )
            else:
                obs_type = ""

        # Если строка — словарь
        elif isinstance(row, dict):

            time_str = row.get(time_col)
            kp_str = row.get(kp_col)

            obs_type = (
                str(row.get(obs_col, "")).lower()
                if obs_col is not None
                else ""
            )

        else:
            continue

        if not time_str or not kp_str:
            continue

        # -----------------------------------------------------
        # Дата и время
        # -----------------------------------------------------

        try:
            time_str = str(time_str).strip()

            if "T" in time_str:
                dt = datetime.fromisoformat(
                    time_str.replace("Z", "+00:00")
                )
            else:
                dt = datetime.strptime(
                    time_str,
                    "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)

        except (ValueError, TypeError):
            continue

        if dt.date() != target_date:
            continue

        # -----------------------------------------------------
        # Kp
        # -----------------------------------------------------

        try:
            kp = math.ceil(float(kp_str))
        except (ValueError, TypeError):
            continue

        rows.append((dt, kp, obs_type))

    # ---------------------------------------------------------
    # Если данных нет
    # ---------------------------------------------------------

    if not rows:
        return (
            f"⚠️ Данные за "
            f"{target_date.strftime('%d.%m.%Y')} "
            f"пока не опубликованы."
        )

    # ---------------------------------------------------------
    # Сортировка
    # ---------------------------------------------------------

    rows.sort(key=lambda x: x[0])

    max_kp = max(kp for _, kp, _ in rows)

    if only_max:
        return max_kp

    # ---------------------------------------------------------
    # Формирование сообщения
    # ---------------------------------------------------------

    date_str = target_date.strftime("%d.%m.%Y")

    lines = [
        f"🧲 *Геомагнитная обстановка — {date_str}*"
    ]

    for dt, kp, obs in rows:

        time_hm = dt.strftime("%H:%M")

        if kp < 4:
            emoji, desc = "🟢", "спокойно"

        elif kp < 5:
            emoji, desc = "🟡", "неустойчиво"

        elif kp < 6:
            emoji, desc = "🟠", "слабая буря (G1)"

        elif kp < 7:
            emoji, desc = "🔴", "умеренная буря (G2)"

        elif kp < 8:
            emoji, desc = "⚫", "сильная буря (G3)"

        else:
            emoji, desc = "💥", "экстремальная буря"

        if "obs" in obs or "real" in obs:
            src = "☑️"

        elif (
            "forecast" in obs
            or "pred" in obs
            or "est" in obs
        ):
            src = "🌓"

        else:
            src = "—"

        lines.append(
            f"{emoji} *{time_hm}* — "
            f"Kp = {kp} → {desc} {src}"
        )

    # ---------------------------------------------------------
    # Итог
    # ---------------------------------------------------------

    if max_kp < 4:
        summary = "🟢 Спокойная геомагнитная обстановка."

    elif max_kp < 5:
        summary = "🟡 Небольшие возмущения."

    elif max_kp < 6:
        summary = "🟠 Слабая буря (G1)."

    elif max_kp < 7:
        summary = "🔴 Умеренная буря (G2)."

    elif max_kp < 8:
        summary = "⚫ Сильная буря (G3)."

    else:
        summary = "⚠️ Экстремальная геомагнитная активность!"

    lines.append("")
    lines.append(f"📌 *Макс. Kp за день*: {max_kp}")
    lines.append(summary)

    return "\n".join(lines)


min_value = "⚠️ У вас стоит минимальное значение"

max_value = "⚠️ У вас стоит максимальное значение"

_order_user = "🧲 Это ваш минимальный порог для уведомлений"

gratitude = "Спасибо, что доверяете нам☺️"
