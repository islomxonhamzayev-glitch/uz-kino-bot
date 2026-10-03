# ============================================================
# UZ KINO BOT — MAJBURIY OBUNA
# Foydalanuvchi botga kirganda majburiy kanallarni ko'rsatadi.
# ============================================================

from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

import sqlite3

from bot.database import get_connection
from bot.keyboards import main_menu


# ============================================================
# 1. ROUTER
# ============================================================

router = Router()


# ============================================================
# 2. KANALLARNI BAZADAN OLISH
# ============================================================

def get_channels():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, chat_id, username, title, invite_link
        FROM channels
        ORDER BY id ASC
    """)

    channels = cursor.fetchall()

    connection.close()

    return channels


# ============================================================
# 3. MAJBURIY OBUNA TUGMALARI
# ============================================================

def subscription_keyboard():

    channels = get_channels()

    buttons = []

    for channel in channels:

        channel_id = channel[0]
        username = channel[2]
        title = channel[3]
        invite_link = channel[4]

        # Kanal uchun havolani aniqlaymiz
        if username:

            username_clean = username.replace("@", "")

            url = f"https://t.me/{username_clean}"

        elif invite_link:

            url = invite_link

        else:

            # Havola bo'lmasa tugma yaratmaymiz
            continue

        # Kanal nomi
        channel_name = title or username or "Kanal"

        buttons.append([
            InlineKeyboardButton(
                text=f"📢 {channel_name}",
                url=url
            )
        ])

    # Tekshirish tugmasi
    buttons.append([
        InlineKeyboardButton(
            text="✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# ============================================================
# 4. FOYDALANUVCHI OBUNA BO'LGANINI TEKSHIRISH
# ============================================================

async def is_user_subscribed(bot, user_id: int):

    channels = get_channels()

    # Agar majburiy kanal umuman bo'lmasa,
    # foydalanuvchini o'tkazamiz.
    if not channels:
        return True

    for channel in channels:

        chat_id = channel[1]

        try:

            member = await bot.get_chat_member(
                chat_id=chat_id,
                user_id=user_id
            )

            # Telegram statuslari
            if member.status in ["left", "kicked"]:
                return False

            # restricted bo'lsa ham member bo'lishi mumkin
            if member.status == "restricted":

                if hasattr(member, "is_member") and not member.is_member:
                    return False

        except Exception:
            # Kanalni tekshirib bo'lmasa,
            # obuna tasdiqlanmagan deb hisoblaymiz.
            return False

    return True


# ============================================================
# 5. "OBUNANI TEKSHIRISH" TUGMASI
# ============================================================

@router.callback_query(F.data == "check_subscription")
async def check_subscription(callback: CallbackQuery):

    user_id = callback.from_user.id

    subscribed = await is_user_subscribed(
        callback.bot,
        user_id
    )

    # Obuna bo'lmagan
    if not subscribed:

        await callback.answer(
            "❌ Hali barcha kanallarga obuna bo'lmagansiz!",
            show_alert=True
        )

        return

    # Obuna to'liq
    await callback.answer(
        "✅ Obuna tasdiqlandi!"
    )

    # Majburiy obuna xabarini asosiy menyuga almashtiramiz
    await callback.message.edit_text(
        "🎬 <b>UZ KINO BOT</b>\n\n"
        "✅ Obunangiz tasdiqlandi!\n\n"
        "🍿 Kerakli bo'limni tanlang:",
        reply_markup=main_menu()
    )
