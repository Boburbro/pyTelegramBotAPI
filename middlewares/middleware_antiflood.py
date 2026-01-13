from loader import bot, l10n

from telebot.asyncio_handler_backends import BaseMiddleware
from telebot.async_telebot import CancelUpdate

import asyncio
import time


class SimpleMiddleware(BaseMiddleware):
    def __init__(
        self,
        limit: int,
        warn_interval: int = 5,
        *,
        action: str = "wait",
        drop_duplicates: bool = True,
        warn_text: str | None = None,
    ) -> None:
        """
        limit         – xabarlar orasidagi minimal ruxsat etilgan vaqt (sekundlarda)
        warn_interval – bitta foydalanuvchiga antiflood xabarini qayta yuborish oralig'i (sekundlarda)
        action        – "wait" (navbatlab kutadi) yoki "drop" (limit ichida kelsa ignore qiladi)
        drop_duplicates – limit ichida bir xil xabar (matn/caption) kelsa ignore qiladi
        warn_text     – agar berilsa, limit ichida kelgan xabarga javoban shu ogohlantirish yuboriladi
        """
        self.last_time = {}
        self.last_warn_time = {}
        self.last_signature = {}
        self._locks = {}
        self.limit = limit
        self.warn_interval = warn_interval
        self.action = action
        self.drop_duplicates = drop_duplicates
        self.warn_text = warn_text
        self.update_types = ["message"]

    def _signature(self, message):
        content_type = getattr(message, "content_type", None)
        text = getattr(message, "text", None)
        caption = getattr(message, "caption", None)
        # For non-text updates, (content_type, caption) still helps dedupe.
        return (content_type, text, caption)

    async def pre_process(self, message, data):
        if len(list(l10n.missing_keys)) > 0:
            print("Missing localization keys:", list(l10n.missing_keys))

        user_id = getattr(message.from_user, "id", None)
        if user_id is None:
            return

        # Per-user queue: ensure we don't start processing multiple updates from
        # the same user too frequently (e.g. 2 messages at 10:15:01 -> 2nd waits).
        lock = self._locks.get(user_id)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[user_id] = lock

        async with lock:
            now = time.monotonic()
            last = self.last_time.get(user_id, 0.0)
            wait_for = (last + float(self.limit)) - now

            if wait_for > 0:
                sig = self._signature(message)
                last_sig = self.last_signature.get(user_id)

                # If it's the same message within the window -> ignore (drop)
                if self.drop_duplicates and last_sig == sig:
                    if self.warn_text:
                        last_warn = self.last_warn_time.get(user_id, 0.0)
                        if (now - last_warn) >= float(self.warn_interval):
                            try:
                                await bot.send_message(message.chat.id, self.warn_text)
                            except Exception:
                                pass
                            self.last_warn_time[user_id] = time.monotonic()
                    return CancelUpdate()

                # Otherwise either wait (recommended) or drop depending on action
                if self.action == "drop":
                    if self.warn_text:
                        last_warn = self.last_warn_time.get(user_id, 0.0)
                        if (now - last_warn) >= float(self.warn_interval):
                            try:
                                await bot.send_message(message.chat.id, self.warn_text)
                            except Exception:
                                pass
                            self.last_warn_time[user_id] = time.monotonic()
                    return CancelUpdate()

                # default: queue (wait)
                await asyncio.sleep(wait_for)

            # Mark the start time of this update processing
            self.last_time[user_id] = time.monotonic()
            self.last_signature[user_id] = self._signature(message)

    async def post_process(self, message, data, exception):
        pass


bot.setup_middleware(SimpleMiddleware(limit=1, action="wait", drop_duplicates=True))
