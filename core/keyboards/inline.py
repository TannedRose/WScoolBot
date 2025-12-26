from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⚙️Настройки", callback_data="settings")],
    [InlineKeyboardButton(text="🔮Прогноз на завтра", callback_data="predict_weather")],
    [InlineKeyboardButton(text="📊Прогноз на сегодня", callback_data="now_weather")],
])

back_to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="◀️Назад", callback_data="back_to_main")],
])


async def settings(notif: bool, queru: bool, order: int):
    keyboard = [
        [InlineKeyboardButton(
            text=f"🔔 Уведомления: {'ON ✅' if notif else 'OFF ❌'}",
            callback_data="notifications"
        )]
    ]

    if notif:
        keyboard.append([
            InlineKeyboardButton(text="➖", callback_data="minus"),
            InlineKeyboardButton(text=f"{order}", callback_data=f"order_user {order}"),
            InlineKeyboardButton(text="➕", callback_data="plus"),
        ])

    keyboard.append([
        InlineKeyboardButton(
            text=f"📝 Опрос: {'ON ✅' if queru else 'OFF ❌'}",
            callback_data="query"
        )
    ])

    keyboard.append([
        InlineKeyboardButton(text="Назад", callback_data="back_to_main")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

