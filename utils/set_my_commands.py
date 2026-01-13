from loader import bot
from telebot.types import BotCommand
import asyncio

async def set_my_commands():
    
    await bot.set_my_commands(
        [
            BotCommand("start", "Botni qayta ishga tushirish"),
            BotCommand("help", "Yordam va qo'llanma"),
            BotCommand("settings", "Sozlamalar"),
        ],
        language_code="uz",
    )

    await bot.set_my_commands(
        [
            BotCommand("start", "Restart the bot"),
            BotCommand("help", "Get help and instructions"),
        ],
        language_code="en",
    )

    await bot.set_my_commands(
        [
            BotCommand("start", "Перезапустить бота"),
            BotCommand("help", "Помощь и руководство"),
        ],
        language_code="ru",
    )


asyncio.run(set_my_commands())