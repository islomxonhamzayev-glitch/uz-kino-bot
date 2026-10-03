
# ============================================================
# UZ KINO BOT — ASOSIY FAYL
# Bu fayl barcha modullarni birlashtirib, botni ishga tushiradi.
# ============================================================

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Bot tokenini config.py dan olamiz
from bot.config import BOT_TOKEN

# Ma'lumotlar bazasi jadvallarini yaratish
from bot.database import create_tables

# Barcha handlerlarni import qilamiz
from bot.handlers import start
from bot.handlers import channels
from bot.handlers import movies
from bot.handlers import user
from bot.handlers import admin
from bot.handlers import settings


# ============================================================
# 1. BOT VA DISPATCHERNI YARATISH
# ============================================================

# HTML formatdagi <b>, <i>, <code> kabi teglarni ishlatish
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)

# Dispatcher — bot kelayotgan xabarlarni handlerlarga tarqatadi
dp = Dispatcher()


# ============================================================
# 2. HANDLERLARNI ULASH
# ============================================================

# Foydalanuvchi /start va asosiy menyu
dp.include_router(start.router)

# Majburiy obuna va kanallar
dp.include_router(channels.router)

# Kino qidirish, top, random, sevimlilar
dp.include_router(movies.router)

# Profil, janrlar, yordam va boshqa user funksiyalar
dp.include_router(user.router)

# Admin panel
dp.include_router(admin.router)

# Bot sozlamalari
dp.include_router(settings.router)


# ============================================================
# 3. BOTNI ISHGA TUSHIRISH
# ============================================================

async def main():

    # Ma'lumotlar bazasidagi jadvallarni yaratamiz
    create_tables()

    # Eski webhook bo'lsa o'chiramiz.
    # Shunda polling bilan konflikt bo'lmaydi.
    await bot.delete_webhook(drop_pending_updates=True)

    print("=" * 50)
    print("🎬 UZ KINO BOT ISHGA TUSHMOQDA...")
    print("=" * 50)

    # Telegramdan yangi xabarlarni doimiy olib turish
    await dp.start_polling(bot)


# ============================================================
# 4. DASturni ISHGA TUSHIRISH
# ============================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n🛑 Bot to'xtatildi.")
