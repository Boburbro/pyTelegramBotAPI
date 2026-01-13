from __future__ import annotations

import asyncio
import threading
import time
from collections import deque
from typing import Any, Callable, Optional


class OutgoingRateLimiter:
    """Simple async rate limiter for outgoing Telegram API calls.

    - Global limit: at most `global_per_sec` sends per second (across all chats)
    - Per-chat limit: at most `per_chat_per_sec` sends per second per chat

    This prevents bursty loops (e.g. asyncio.gather) from sending 30+/sec.
    """

    def __init__(
        self,
        *,
        global_per_sec: float = 30.0,
        per_chat_per_sec: float = 2.0,
    ) -> None:
        if global_per_sec <= 0:
            raise ValueError("global_per_sec must be > 0")
        if per_chat_per_sec <= 0:
            raise ValueError("per_chat_per_sec must be > 0")

        self._global_interval = 1.0 / float(global_per_sec)
        self._chat_interval = 1.0 / float(per_chat_per_sec)

        self._lock = asyncio.Lock()
        self._global_next_at = 0.0
        self._chat_next_at: dict[Any, float] = {}

    async def acquire(self, chat_id: Optional[Any] = None) -> None:
        async with self._lock:
            now = time.monotonic()
            earliest = now

            if self._global_next_at > earliest:
                earliest = self._global_next_at

            if chat_id is not None:
                chat_next = self._chat_next_at.get(chat_id, now)
                if chat_next > earliest:
                    earliest = chat_next

            self._global_next_at = earliest + self._global_interval
            if chat_id is not None:
                self._chat_next_at[chat_id] = earliest + self._chat_interval

            delay = earliest - now

        if delay > 0:
            await asyncio.sleep(delay)


def _extract_chat_id(args: tuple[Any, ...], kwargs: dict[str, Any]) -> Optional[Any]:
    if "chat_id" in kwargs:
        return kwargs.get("chat_id")
    if len(args) >= 1:
        return args[0]
    return None


_history_lock = threading.Lock()
_outgoing_history: deque[tuple[int, int, int]] = deque(maxlen=10)


def get_outgoing_history(limit: int = 10) -> list[tuple[int, int, int]]:
    """Return list of (epoch_sec, count) for last seconds, newest last."""

    with _history_lock:
        data = list(_outgoing_history)[-limit:]
    return data


def patch_outgoing(
    bot: Any,
    limiter: OutgoingRateLimiter,
    *,
    methods: tuple[str, ...] = (
        "send_message",
        "send_photo",
        "send_video",
        "send_document",
        "send_audio",
        "send_voice",
        "send_animation",
        "send_media_group",
        "copy_message",
    ),
) -> None:
    """Monkey-patch AsyncTeleBot send_* methods to be rate-limited."""

    stats_lock = asyncio.Lock()
    stats_sec = int(time.time())
    stats_count = 0
    max_count = 0

    for method_name in methods:
        original = getattr(bot, method_name, None)
        if original is None:
            continue

        async def _wrapper(
            *args: Any,
            __orig: Callable[..., Any] = original,
            **kwargs: Any,
        ) -> Any:
            nonlocal stats_sec, stats_count, max_count
            chat_id = _extract_chat_id(args, kwargs)
            await limiter.acquire(chat_id)

            now_sec = int(time.time())
            async with stats_lock:
                if now_sec != stats_sec:
                    ts = time.strftime("%Y.%m.%d %H:%M:%S", time.localtime(stats_sec))
                    if stats_count:
                        with _history_lock:
                            if max_count < stats_count:
                                max_count = stats_count
                            _outgoing_history.append((stats_sec, stats_count, max_count))
                        print(f"{ts} {stats_count} message", flush=True)
                    stats_sec = now_sec
                    stats_count = 0
                stats_count += 1

            return await __orig(*args, **kwargs)

        setattr(bot, method_name, _wrapper)
