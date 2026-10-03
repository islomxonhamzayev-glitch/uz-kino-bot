# ============================================================
# UZ KINO BOT
# 1-FAYL: config.py
# ============================================================
#
# Bu faylda botning asosiy sozlamalari saqlanadi.
#
# BOT_TOKEN:
#   Telegram BotFather bergan bot tokeni.
#
# ADMIN_ID:
#   Botni boshqaradigan administratorning Telegram ID raqami.
#
# Muhim:
#   Tokenni hech kimga yubormang va GitHub kabi ochiq joyga
#   joylamang.
# ============================================================

import os

from dotenv import load_dotenv


# .env faylidagi ma'lumotlarni Python dasturiga yuklaymiz
load_dotenv()


# Telegram bot tokeni
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Asosiy administratorning Telegram ID raqami
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))


# Ma'lumotlar bazasi faylining nomi
DATABASE_NAME = "kino.db"


# Agar token topilmasa, dastur xato chiqaradi
if not BOT_TOKEN:
    raise ValueError(
        "BOT_TOKEN topilmadi! .env faylni tekshiring."
    )


# Agar ADMIN_ID noto'g'ri bo'lsa, dastur ogohlantiradi
if ADMIN_ID == 0:
    raise ValueError(
        "ADMIN_ID topilmadi! .env faylni tekshiring."
    )
