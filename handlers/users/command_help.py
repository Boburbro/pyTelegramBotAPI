from loader import bot, l10n
from telebot.types import Message

@bot.message_handler(commands=['help'])
async def command_help(message: Message):
    await bot.send_message(chat_id = message.chat.id, text = l10n.t("help"))