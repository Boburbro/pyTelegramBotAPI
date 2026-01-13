from loader import bot, l10n
from telebot.types import Message

@bot.message_handler(commands=['start'])
async def command_start(message: Message):
    await bot.send_message(chat_id = message.chat.id, text = l10n.t("greeting", name=message.from_user.first_name))
