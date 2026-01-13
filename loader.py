from telebot.async_telebot import AsyncTeleBot, ExceptionHandler
from data.config import BOT_TOKEN, LANG_CODE
from helper.message_sender import OutgoingRateLimiter, patch_outgoing
from helper.localization.l10n import L10n


l10n = L10n(lang_code=LANG_CODE)

_outgoing_limiter = OutgoingRateLimiter()

bot = AsyncTeleBot(BOT_TOKEN, exception_handler=ExceptionHandler(), parse_mode=None)

patch_outgoing(bot, _outgoing_limiter)
