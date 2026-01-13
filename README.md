<h1 align="center">PyTelegramBotAPI Template</h1>

Minimal, toza va kengaytiriladigan **Telegram bot shabloni** (AsyncTeleBot / pyTelegramBotAPI).

## Nimalar bor?

- **Async** bot (`telebot.async_telebot.AsyncTeleBot`)
- Handlerlar bo'limlarga ajratilgan: `handlers/users`, `handlers/groups`, `handlers/channels`
- **Localization (i18n)**: `helper/localization` (`uz`, `en`, `ru`)
- **Anti-flood middleware**: foydalanuvchining tez-tez yuborgan xabarlarini navbatlab kutadi yoki drop qiladi
- **Outgoing rate limiter**: botning `send_*` metodlarini rate-limit qilib, Telegram limitlariga moslashtiradi

## Talablar

- Python 3.10+ (tavsiya)
- Telegram bot token (BotFather)

## Tezkor start

```bash
git clone https://github.com/Boburbro/pyTelegramBotAPI bot
cd bot

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env
```

`.env` ichida eng muhimi: `BOT_TOKEN`.

So'ng botni ishga tushiring:

```bash
python bot.py
```

## Konfiguratsiya (`.env`)

Shablonda sozlamalar [data/config.py](data/config.py) orqali olinadi.

Minimal misol:

```env
BOT_TOKEN=1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi
ADMINS=12345678,87654321
LANG_CODE=uz
ip=localhost
```

- `BOT_TOKEN` – majburiy
- `ADMINS` – ixtiyoriy (admin user id lar, vergul bilan)
- `LANG_CODE` – default til: `uz` / `en` / `ru`
- `ip` – ixtiyoriy (hozircha faqat config’da bor; webhook/server uchun ishlatishingiz mumkin)

## Arxitektura (qisqacha)

- Bot instance: [loader.py](loader.py)
- Entry point: [bot.py](bot.py)
- Handlerlar: [handlers/](handlers/)
- Middleware: [middlewares/](middlewares/)
- Lokalizatsiya fayllari: [helper/localization/locales/](helper/localization/locales/)

`bot.py` ishga tushganda:

1) `middlewares`, `filters`, `handlers` import qilinadi (register bo'lishi uchun)
2) `set_my_commands()` – bot commandlar o'rnatiladi
3) `notify_admins()` – adminlarga “bot ishga tushdi” xabari yuboriladi
4) `infinity_polling()` – polling start

## Yangi handler qo'shish

1) Masalan, `handlers/users/command_ping.py` yarating:

```python
from loader import bot
from telebot.types import Message

@bot.message_handler(commands=["ping"])
async def ping(message: Message):
	await bot.send_message(message.chat.id, "pong")
```

2) Uni [handlers/users/__init__.py](handlers/users/__init__.py) ichiga import qiling:

```python
from . import command_ping
```

## Lokalizatsiya (i18n)

Tarjimalar JSON orqali:

- [helper/localization/locales/uz.json](helper/localization/locales/uz.json)
- [helper/localization/locales/en.json](helper/localization/locales/en.json)
- [helper/localization/locales/ru.json](helper/localization/locales/ru.json)

Koddan chaqirish:

```python
from loader import l10n

text = l10n.t("greeting", name="Bobur")
```

Middleware har bir update’da `missing_keys` ni tekshiradi va topilmagan key’larni konsolga chiqaradi.

## Anti-flood middleware

Middleware fayli: [middlewares/middleware_antiflood.py](middlewares/middleware_antiflood.py)

Default sozlama:

- `limit=1` (1 sekund)
- `action="wait"` (xabarlar navbatda kutadi)
- `drop_duplicates=True` (limit ichida bir xil xabar bo'lsa drop)

## Foydali eslatmalar

- `utils/set_my_commands.py` va `utils/notify_admins.py` endi **import paytida ishlamaydi**; startup’da [bot.py](bot.py) ichidan chaqiriladi.
- Agar adminlar bo'sh bo'lsa (`ADMINS=[]`) — notify shunchaki hech narsa yubormaydi.

## Troubleshooting

- `BOT_TOKEN` noto'g'ri bo'lsa: Bot pollingda xatolik beradi. Tokenni qayta tekshiring.
- `.env` o'qilmayotgan bo'lsa: fayl nomi aynan `.env` ekanini va projekt root’da turganini tekshiring.