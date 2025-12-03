import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple, Dict, Any



setup = """
⚙️ Настройки

✨ Уведомления (8:00)  
📅 Утром получите прогноз на день  

✨ Опрос (20:00)  
🌙 Вечером бот спросит о вашем самочувствии
"""


main = """
✅ Вы в главном меню
"""


async def get_kp_forecast_report(days_ahead: int = 0, only_max: bool = False):
    url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return f"❌ Ошибка загрузки данных: {e}"

    if not data or len(data) < 2:
        return "❌ Пустой ответ от NOAA."

    headers = data[0]
    # Гибкий поиск столбцов — на случай переименований
    try:
        time_col = next(i for i, h in enumerate(headers) if
                        'time' in h.lower() and ('tag' in h.lower() or h.lower() in {'time', 'timestamp'}))
        kp_col = next(i for i, h in enumerate(headers) if 'kp' in h.lower())
        obs_col = next((i for i, h in enumerate(headers) if 'obs' in h.lower() or 'status' in h.lower()), None)
    except StopIteration:
        return f"❌ Не найдены столбцы. Заголовки: {headers}"

    target_date = (datetime.now(timezone.utc).date() + timedelta(days=days_ahead))
    target_rows: List[Tuple[datetime, float, str]] = []

    for row in data[1:]:
        if len(row) <= max(time_col, kp_col):
            continue

        time_str = row[time_col]
        kp_str = row[kp_col]
        obs_type = row[obs_col].lower() if obs_col is not None and row[obs_col] else "unknown"

        if not time_str or not kp_str:
            continue

        try:
            # Поддерживаем оба формата: "2025-11-21 00:00:00" и "2025-11-21T00:00:00Z"
            if 'T' in time_str:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(time_str.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        except Exception:
            continue

        if dt.date() != target_date:
            continue

        try:
            kp = float(kp_str)
        except (ValueError, TypeError):
            continue

        target_rows.append((dt, kp, obs_type))

    if not target_rows:
        date_fmt = target_date.strftime("%d.%m.%Y")
        return f"⚠️ Данные за {date_fmt} пока не опубликованы."

    target_rows.sort(key=lambda x: x[0])
    date_str = target_date.strftime("%d.%m.%Y")

    lines = [f"🧲 *Геомагнитная обстановка — {date_str}*"]

    max_kp = max(kp for _, kp, _ in target_rows)

    for dt, kp, obs_type in target_rows:
        time_hm = dt.strftime("%H:%M")

        # Эмодзи и описание
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
        elif kp < 9:
            emoji, desc = "🟣", "очень сильная (G4)"
        else:
            emoji, desc = "💥", "экстремальная (G5)"

        # Источник
        if 'obs' in obs_type or 'real' in obs_type:
            src = "✅"
        elif 'est' in obs_type or 'pred' in obs_type or 'forecast' in obs_type:
            src = "🌓"
        else:
            src = "—"

        lines.append(f"{emoji} *{time_hm}* — Kp = {kp:.2g} → {desc} ({src})")

    if max_kp < 4:
        summary = "🟢 В целом — спокойная геомагнитная обстановка. Подходит для наблюдений за северным сиянием на высоких широтах."
    elif max_kp < 5:
        summary = "🟡 Небольшие возмущения. Возможны слабые проявления полярных сияний."
    elif max_kp < 6:
        summary = "🟠 Слабая геомагнитная буря (G1). Сияния возможны уже на широте Санкт-Петербурга и Минска."
    elif max_kp < 7:
        summary = "🔴 Умеренная буря (G2). Сияния могут наблюдаться до Москвы и Киева. Возможны кратковременные перебои в КВ-связи."
    elif max_kp < 8:
        summary = "⚫ Сильная буря (G3). Возможны сбои в спутниковой навигации и на ЛЭП. Яркие сияния — до юга Европы."
    else:
        summary = "⚠️⚠️⚠️ Экстремальная геомагнитная активность! Возможны масштабные технологические последствия. Сияния — даже в средних широтах."

    lines.append("")
    lines.append(f"📌 *Макс. Kp за день*: {max_kp:.2g} → {summary}")
    if only_max:
        return max_kp
    else:
        return "\n".join(lines)
