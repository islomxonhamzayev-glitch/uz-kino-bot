# ============================================================
# UZ KINO BOT
# 13-FAYL: handlers/settings.py
# ============================================================
#
# Bu fayl BOTNING O'Z SOZLAMALARINI boshqaradi.
#
# Admin quyidagilarni o'zgartira oladi:
#
# ✏️ Bot nomi
# 📝 Bot description
# ℹ️ Bot About
# 🖼 Bot profil rasmi
#
# ============================================================

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputFile
)

from bot.config import ADMIN_ID
from bot.states import BotSettingsState


# ============================================================
# ROUTER
# ============================================================

router = Router()


# ============================================================
# ADMINNI TEKSHIRISH
# ============================================================

def is_admin(user_id: int):

    return user_id == ADMIN_ID


# ============================================================
# BOT SOZLAMALARI MENYUSI
# ============================================================

def settings_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="✏️ Bot nomi",
                    callback_data="bot_name"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📝 Description",
                    callback_data="bot_description"
                )
            ],

            [
                InlineKeyboardButton(
                    text="ℹ️ About",
                    callback_data="bot_about"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🖼 Profil rasmi",
                    callback_data="bot_photo"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅️ Admin panel",
                    callback_data="back_admin"
                )
            ]

        ]
    )


# ============================================================
# 1. BOT SOZLAMALARINI OCHISH
# ============================================================

@router.callback_query(
    F.data == "bot_settings"
)
async def bot_settings(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🤖 <b>BOT SOZLAMALARI</b>\n\n"
        "O'zgartirmoqchi bo'lgan bo'limni tanlang:",
        reply_markup=settings_menu()
    )

    await callback.answer()


# ============================================================
# 2. BOT NOMINI O'ZGARTIRISH
# ============================================================

@router.callback_query(
    F.data == "bot_name"
)
async def bot_name_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        BotSettingsState.waiting_name
    )

    await callback.message.answer(
        "✏️ <b>BOT NOMI</b>\n\n"
        "Yangi bot nomini yuboring.\n\n"
        "Masalan:\n"
        "<code>UZ KINO 🎬</code>"
    )

    await callback.answer()


@router.message(
    BotSettingsState.waiting_name
)
async def set_bot_name(
    message: Message,
    state: FSMContext,
    bot
):

    if not is_admin(message.from_user.id):
        return

    name = message.text.strip()

    try:

        await bot.set_my_name(
            name=name
        )

        await message.answer(
            "✅ <b>Bot nomi o'zgartirildi!</b>\n\n"
            f"🤖 Yangi nom: <b>{name}</b>"
        )

    except Exception as error:

        await message.answer(
            "❌ Bot nomini o'zgartirishda xatolik:\n\n"
            f"<code>{error}</code>"
        )

    await state.clear()


# ============================================================
# 3. BOT DESCRIPTION
# ============================================================

@router.callback_query(
    F.data == "bot_description"
)
async def bot_description_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        BotSettingsState.waiting_description
    )

    await callback.message.answer(
        "📝 <b>BOT DESCRIPTION</b>\n\n"
        "Bot haqida qisqacha ma'lumot yuboring.\n\n"
        "Masalan:\n"
        "<code>🎬 Eng yangi kinolarni bizning bot orqali toping!</code>"
    )

    await callback.answer()


@router.message(
    BotSettingsState.waiting_description
)
async def set_bot_description(
    message: Message,
    state: FSMContext,
    bot
):

    if not is_admin(message.from_user.id):
        return

    description = message.text.strip()

    try:

        await bot.set_my_description(
            description=description
        )

        await message.answer(
            "✅ <b>Description o'zgartirildi!</b>"
        )

    except Exception as error:

        await message.answer(
            "❌ Description o'zgartirishda xatolik:\n\n"
            f"<code>{error}</code>"
        )

    await state.clear()


# ============================================================
# 4. BOT ABOUT
# ============================================================

@router.callback_query(
    F.data == "bot_about"
)
async def bot_about_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        BotSettingsState.waiting_about
    )

    await callback.message.answer(
        "ℹ️ <b>BOT ABOUT</b>\n\n"
        "Bot profilida ko'rinadigan qisqa matnni yuboring.\n\n"
        "Masalan:\n"
        "<code>🎬 UZ KINO — kino olamidagi eng yaxshi tanlov.</code>"
    )

    await callback.answer()


@router.message(
    BotSettingsState.waiting_about
)
async def set_bot_about(
    message: Message,
    state: FSMContext,
    bot
):

    if not is_admin(message.from_user.id):
        return

    about = message.text.strip()

    try:

        await bot.set_my_short_description(
            short_description=about
        )

        await message.answer(
            "✅ <b>About o'zgartirildi!</b>"
        )

    except Exception as error:

        await message.answer(
            "❌ About o'zgartirishda xatolik:\n\n"
            f"<code>{error}</code>"
        )

    await state.clear()


# ============================================================
# 5. BOT PROFIL RASMINI O'ZGARTIRISH
# ============================================================
#
# Admin rasm yuboradi.
#
# Telegram bot profil rasmini o'zgartirish uchun rasmni
# Telegram serveridan olib, Bot API orqali yuboramiz.
#
# Bu qism aiogram versiyasiga bog'liq bo'lishi mumkin.
# Shuning uchun avval rasmni qabul qilish va saqlash
# jarayonini tayyorlaymiz.
# ============================================================

@router.callback_query(
    F.data == "bot_photo"
)
async def bot_photo_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        BotSettingsState.waiting_photo
    )

    await callback.message.answer(
        "🖼 <b>BOT PROFIL RASMI</b>\n\n"
        "Yangi profil rasmini yuboring.\n\n"
        "📌 Rasmni oddiy <b>Photo</b> sifatida yuboring."
    )

    await callback.answer()


# ============================================================
# RASMNI QABUL QILISH
# ============================================================

@router.message(
    BotSettingsState.waiting_photo,
    F.photo
)
async def receive_bot_photo(
    message: Message,
    state: FSMContext,
    bot
):

    if not is_admin(message.from_user.id):
        return

    try:

        # Eng katta sifatdagi rasmni olamiz
        photo = message.photo[-1]

        # Telegramdan fayl ma'lumotlarini olamiz
        file = await bot.get_file(
            photo.file_id
        )

        # Rasmni vaqtinchalik joyga yuklaymiz
        photo_path = "bot_profile.jpg"

        await bot.download_file(
            file.file_path,
            destination=photo_path
        )

        await message.answer(
            "✅ Rasm qabul qilindi.\n\n"
            "🖼 Rasm serverga saqlandi."
        )

    except Exception as error:

        await message.answer(
            "❌ Rasmni olishda xatolik:\n\n"
            f"<code>{error}</code>"
        )

    await state.clear()


# ============================================================
# RASM YUBORILMAGAN HOLAT
# ============================================================

@router.message(
    BotSettingsState.waiting_photo
)
async def wrong_photo_format(
    message: Message
):

    await message.answer(
        "❌ Iltimos, rasmni <b>Photo</b> ko'rinishida yuboring."
    )
