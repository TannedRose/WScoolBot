import requests
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple, Dict, Any


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
            src = "📊 наблюдено"
        elif 'est' in obs_type or 'pred' in obs_type or 'forecast' in obs_type:
            src = "🔮 прогноз"
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



# def get_weather_and_geomag_report(
#     lat: float = 55.1815,  # Витебск, Беларусь
#     lon: float = 30.2073,
#     tz: str = "Europe/Minsk"
# ) -> Optional[Dict[str, Any]]:
#     """
#     Получает полный отчёт о погоде и геомагнитной обстановке.
#     Возвращает словарь с ключами:
#         - temperature: float (°C)
#         - pressure: float (гПа)
#         - humidity: int (%)
#         - wind_speed: float (м/с)
#         - wind_direction: int (градусы)
#         - wind_direction_str: str ("С", "Ю-З" и т.д.)
#         - kp: float (Kp-индекс)
#         - kp_level: str ("спокойно", "буря G2" и т.д.)
#         - kp_emoji: str ("🟢", "🔴")
#         - temp_change_12h: float (ΔT за 12ч, °C)
#         - temp_change_24h: float (ΔT за 24ч, °C)
#         - rapid_change: bool (резкий перепад? |ΔT| ≥ 5°C/12ч)
#     """
#     try:
#         # 1️⃣ Погода: Open-Meteo (бесплатно, без ключа)
#         weather_url = (
#             f"https://api.open-meteo.com/v1/forecast"
#             f"?latitude={lat}&longitude={lon}"
#             f"&current=temperature_2m,relative_humidity_2m,pressure_msl,wind_speed_10m,wind_direction_10m"
#             f"&hourly=temperature_2m"
#             f"&forecast_days=2"
#             f"&timezone={tz}"
#         )
#         w_resp = requests.get(weather_url, timeout=10)
#         w_resp.raise_for_status()
#         w_data = w_resp.json()
#
#         cur = w_data["current"]
#         temp = cur["temperature_2m"]
#         humidity = int(cur["relative_humidity_2m"])
#         pressure = cur["pressure_msl"]  # в гПа (мбар)
#         wind_speed = cur["wind_speed_10m"]
#         wind_dir = cur["wind_direction_10m"]
#
#         # Направление ветра → строка
#         def degrees_to_direction(deg: float) -> str:
#             dirs = ["С", "С-В", "В", "Ю-В", "Ю", "Ю-З", "З", "С-З"]
#             idx = round(deg / 45) % 8
#             return dirs[idx]
#
#         wind_dir_str = degrees_to_direction(wind_dir)
#
#         # Температурные перепады: смотрим изменение за 12 и 24 часа
#         hourly_temps = w_data["hourly"]["temperature_2m"]
#         temp_now = hourly_temps[-1]
#         temp_12h_ago = hourly_temps[-13] if len(hourly_temps) >= 14 else temp_now
#         temp_24h_ago = hourly_temps[-25] if len(hourly_temps) >= 26 else temp_now
#
#         delta_12h = temp_now - temp_12h_ago
#         delta_24h = temp_now - temp_24h_ago
#         rapid_change = abs(delta_12h) >= 5.0
#
#         # 2️⃣ Геомагнитная активность: GFZ Potsdam (kpindex.org)
#         today = datetime.now(timezone.utc).date()
#         kp_url = f"https://kpindex.org/api/v1/kp?from={today}&to={today}"
#         kp_resp = requests.get(kp_url, timeout=10)
#         kp_resp.raise_for_status()
#         kp_data = kp_resp.json()
#
#         kp = 3.0  # fallback
#         kp_type = "unknown"
#         if kp_data and isinstance(kp_data, list):
#             # Берём последнее актуальное (обычно 00:00 или 03:00 UTC)
#             latest = max(kp_data, key=lambda x: x.get("datetime", ""))
#             kp = float(latest.get("kp", 3.0))
#             kp_type = latest.get("type", "unknown")
#
#         # Уровень активности
#         if kp < 4:
#             kp_level = "спокойно"
#             kp_emoji = "🟢"
#         elif kp < 5:
#             kp_level = "неустойчиво"
#             kp_emoji = "🟡"
#         elif kp < 6:
#             kp_level = "слабая буря (G1)"
#             kp_emoji = "🟠"
#         elif kp < 7:
#             kp_level = "умеренная буря (G2)"
#             kp_emoji = "🔴"
#         elif kp < 8:
#             kp_level = "сильная буря (G3)"
#             kp_emoji = "⚫"
#         elif kp < 9:
#             kp_level = "очень сильная (G4)"
#             kp_emoji = "🟣"
#         else:
#             kp_level = "экстремальная (G5)"
#             kp_emoji = "💥"
#
#         return {
#             "temperature": round(temp, 1),
#             "pressure": round(pressure, 1),
#             "humidity": humidity,
#             "wind_speed": round(wind_speed, 1),
#             "wind_direction": round(wind_dir),
#             "wind_direction_str": wind_dir_str,
#             "kp": round(kp, 2),
#             "kp_level": kp_level,
#             "kp_emoji": kp_emoji,
#             "kp_type": kp_type,
#             "temp_change_12h": round(delta_12h, 1),
#             "temp_change_24h": round(delta_24h, 1),
#             "rapid_change": rapid_change,
#             "location": f"{lat:.2f}°N, {lon:.2f}°E",
#             "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
#         }
#
#     except Exception as e:
#         print(f"❌ Ошибка получения данных: {e}")
#         return None
#
#
# def format_report(data: dict) -> str:
#     """Форматирует отчёт в красивый вид для Telegram."""
#     if not data:
#         return "⚠️ Данные временно недоступны."
#
#     lines = [
#         f"🌤 *Погода и среда — {data['timestamp']}*",
#         "",
#         f"📍 *Местоположение*: {data['location']}",
#         "",
#         f"🌡 *Температура*: {data['temperature']}°C",
#         f"💧 *Влажность*: {data['humidity']}%",
#         f"🔽 *Давление*: {data['pressure']} гПа",
#         f"💨 *Ветер*: {data['wind_speed']} м/с, {data['wind_direction_str']} ({data['wind_direction']}°)",
#         "",
#         f"🧲 *Геомагнитная активность*: {data['kp_emoji']} Kp = {data['kp']} → {data['kp_level']}",
#         f"   (источник: {'наблюдено' if data['kp_type'] == 'definitive' else 'прогноз'})",
#         ""
#     ]
#
#     # Перепады температуры
#     d12, d24 = data["temp_change_12h"], data["temp_change_24h"]
#     if data["rapid_change"]:
#         lines.append(f"⚠️ *Резкий перепад температуры*: {d12:+.1f}°C за 12 часов!")
#     else:
#         lines.append(f"📈 *Изменение температуры*: {d12:+.1f}°C (12ч), {d24:+.1f}°C (24ч)")
#
#     # Рекомендации (опционально)
#     recs = []
#     if data["kp"] >= 5:
#         recs.append("Следите за самочувствием при метеозависимости.")
#     if data["rapid_change"]:
#         recs.append("Рекомендуется избегать переохлаждения/перегрева.")
#     if data["wind_speed"] > 10:
#         recs.append("Сильный ветер — будьте осторожны на улице.")
#
#     if recs:
#         lines.append("\n💡 *Рекомендации:*")
#         for r in recs:
#             lines.append(f" • {r}")
#
#     return "\n".join(lines)
#
#
# # Пример использования:
# if __name__ == "__main__":
#     print("Запрашиваем данные...")
#     report_data = get_weather_and_geomag_report()
#     if report_data:
#         print(format_report(report_data))
#     else:
#         print("Не удалось получить данные.")