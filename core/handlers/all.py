from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram import Bot, Router, F
import core.keyboards.inline as ikb
import core.database.requests as rq
import core.handlers.texts as txt


router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(txt.start, reply_markup=ikb.main)
    await rq.create_user_with_profile(message.from_user.id, message.from_user.username)

@router.callback_query(F.data == "predict_weather")
async def predict_weather(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    text = await txt.get_kp_forecast_report(days_ahead=1)
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=text,
                                reply_markup=ikb.back_to_main)
@router.callback_query(F.data == "now_weather")
async def now_weather(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    text = await txt.get_kp_forecast_report(days_ahead=0)
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=text,
                                reply_markup=ikb.back_to_main)


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=txt.main,
                                reply_markup=ikb.main)



@router.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    profile = await rq.get_profile_by_tg_id(callback.from_user.id)
    keyboard = await ikb.settings(profile[0], profile[1])
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=txt.setup,
                                reply_markup=keyboard)

@router.callback_query(F.data == "notifications")
async def notifications(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await rq.toggle_profile_flag(callback.from_user.id, "notifications")
    profile = await rq.get_profile_by_tg_id(callback.from_user.id)
    keyboard = await ikb.settings(profile[0], profile[1])
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=txt.setup,
                                reply_markup=keyboard)

@router.callback_query(F.data == "query")
async def notifications(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    await rq.toggle_profile_flag(callback.from_user.id, "query")
    profile = await rq.get_profile_by_tg_id(callback.from_user.id)
    keyboard = await ikb.settings(profile[0], profile[1])
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=txt.setup,
                                reply_markup=keyboard)


@router.callback_query(F.data.startswith("query"))
async def all_good(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    kp = await txt.get_kp_forecast_report(only_max=True)
    health = callback.data.split()[-1]
    await rq.update_query_by_tg_id(user_tg_id=callback.from_user.id, kp=kp, query=health)
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=callback.message.message_id,
                                text=txt.gratitude, reply_markup=ikb.main)
