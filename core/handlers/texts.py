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

    # --- загрузка данных (НЕ блокирует event loop) ---
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

    try:
        time_col = next(
            i for i, h in enumerate(headers)
            if "time" in h.lower()
        )
        kp_col = next(
            i for i, h in enumerate(headers)
            if "kp" in h.lower()
        )
        obs_col = next(
            (i for i, h in enumerate(headers)
             if "obs" in h.lower() or "forecast" in h.lower() or "status" in h.lower()),
            None
        )
    except StopIteration:
        return f"❌ Не найдены нужные столбцы. Заголовки: {headers}"

    target_date = (datetime.now(timezone.utc).date() + timedelta(days=days_ahead))
    rows: List[Tuple[datetime, int, str]] = []

    for row in data[1:]:
        if len(row) <= max(time_col, kp_col):
            continue

        time_str = row[time_col]
        kp_str = row[kp_col]
        obs_type = row[obs_col].lower() if obs_col is not None and row[obs_col] else ""

        if not time_str or not kp_str:
            continue

        try:
            if "T" in time_str:
                dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            else:
                dt = datetime.strptime(
                    time_str.strip(), "%Y-%m-%d %H:%M:%S"
                ).replace(tzinfo=timezone.utc)
        except Exception:
            continue

        if dt.date() != target_date:
            continue

        try:
            kp = math.ceil(float(kp_str))  # безопаснее для Kp
        except (ValueError, TypeError):
            continue

        rows.append((dt, kp, obs_type))

    if not rows:
        return f"⚠️ Данные за {target_date.strftime('%d.%m.%Y')} пока не опубликованы."

    rows.sort(key=lambda x: x[0])

    max_kp = max(kp for _, kp, _ in rows)
    if only_max:
        return max_kp

    date_str = target_date.strftime("%d.%m.%Y")
    lines = [f"🧲 *Геомагнитная обстановка — {date_str}*"]

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
        elif "forecast" in obs or "pred" in obs or "est" in obs:
            src = "🌓"
        else:
            src = "—"

        lines.append(f"{emoji} *{time_hm}* — Kp = {kp} → {desc} {src}")

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