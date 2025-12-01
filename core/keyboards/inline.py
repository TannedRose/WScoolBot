from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚙️Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="🔮Прогноз на завтра", callback_data="predict_weather")],
    [InlineKeyboardButton(text="📊Прогноз на сегодня", callback_data="now_weather")],
])

back_to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️Назад", callback_data="back_to_main")],
])


async def settings(notif: bool, queru: bool):
    return InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=f"Уведомления: {'ON ✅' if notif else 'OFF ❌'}", callback_data="notifications")],
    [InlineKeyboardButton(text=f"Опрос: {'ON ✅' if queru else 'OFF ❌'}", callback_data="query")],
    [InlineKeyboardButton(text="Назад", callback_data="back_to_main")],
])
