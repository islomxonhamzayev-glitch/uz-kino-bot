# ============================================================
# UZ KINO BOT — START
# Foydalanuvchi /start bosganda ishlaydi.
# ============================================================

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.services.user_service import save_user

from bot.handlers.channels import (
    get_channels,
    is_user_subscribed,
    subscription_keyboard
)

from bot.keyboards import main_menu


# ============================================================
# 1. ROUTER
# ============================================================

router = Router()


# ============================================================
# 2. /START
# ============================================================

@router.message(CommandStart())
async def start_handler(
    message: Message
):

    user = message.from_user

    # Foydalanuvchini bazaga saqlaymiz
    save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    # Majburiy kanallar mavjudligini tekshiramiz
    channels = get_channels()

    # Agar admin hali hech qanday kanal qo'shmagan bo'lsa
    if not channels:

        await message.answer(
            "🎬 <b>UZ KINO BOT</b>\n\n"
            "🍿 Xush kelibsiz!\n\n"
            "Kerakli bo'limni tanlang:",
            reply_markup=main_menu()
        )

        return

    # Foydalanuvchi allaqachon obuna bo'lganmi?
    subscribed = await is_user_subscribed(
        message.bot,
        user.id
    )

    # ========================================================
    # OBUNA BO'LMAGAN
    # ========================================================

    if not subscribed:

        await message.answer(
            "🔒 <b>UZ KINO BOT</b>\n\n"
            "🎬 Kinolardan foydalanish uchun "
            "quyidagi kanallarga obuna bo'ling.\n\n"
            "1️⃣ Kanal tugmasini bosing\n"
            "2️⃣ Kanalga obuna bo'ling\n"
            "3️⃣ Barcha kanallarga obuna bo'lgach "
            "✅ <b>Obunani tekshirish</b> tugmasini bosing.",
            reply_markup=subscription_keyboard()
        )

        return

    # ========================================================
    # OBUNA BO'LGAN
    # ========================================================

    await message.answer(
        "🎬 <b>UZ KINO BOT</b>\n\n"
        "👋 Xush kelibsiz!\n\n"
        "🍿 Kerakli bo'limni tanlang:",
        reply_markup=main_menu()
    )
