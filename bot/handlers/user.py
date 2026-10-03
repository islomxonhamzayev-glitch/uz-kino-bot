# ============================================================
# UZ KINO BOT
# 11-FAYL: handlers/user.py
# ============================================================
#
# Bu fayl FOYDALANUVCHINING SHAXSIY BO'LIMI uchun javob beradi.
#
# Bu yerda:
#
# 👤 Profil
# 📊 Shaxsiy statistika
# ❤️ Sevimlilar
# 🔗 Do'stlarni taklif qilish
# 🆘 Yordam
# 🎭 Janrlar
#
# kabi bo'limlar ishlaydi.
# ============================================================


from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from bot.services.user_service import (
    get_user,
    get_users_count,
    get_referral_count,
    get_favorites_count
)


# ============================================================
# ROUTER
# ============================================================
#
# Bu router foydalanuvchining shaxsiy bo'limlari bilan
# bog'liq tugmalarni boshqaradi.
# ============================================================

router = Router()


# ============================================================
# 1. PROFIL MENYUSI
# ============================================================

def profile_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❤️ Sevimlilar",
                    callback_data="favorites"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔗 Do'stlarni taklif qilish",
                    callback_data="referral"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Bosh menyu",
                    callback_data="main_menu"
                )
            ]
        ]
    )


# ============================================================
# 2. FOYDALANUVCHI PROFILI
# ============================================================
#
# Foydalanuvchi "👤 Profil" tugmasini bosganda ishlaydi.
#
# Profil ichida:
#
# 👤 Ism
# 🆔 Telegram ID
# ❤️ Sevimli kinolar
# 👥 Referral
#
# ko'rsatiladi.
# ============================================================

@router.callback_query(
    F.data == "profile"
)
async def profile_handler(
    callback: CallbackQuery
):

    user_id = callback.from_user.id

    # Bazadan foydalanuvchini olamiz
    user = get_user(user_id)

    # Agar qandaydir sabab bilan bazada bo'lmasa,
    # callback orqali kelgan ma'lumotdan foydalanamiz.
    if user:

        saved_user_id = user[0]
        username = user[1]
        first_name = user[2]
        referrals = user[4]

    else:

        saved_user_id = user_id
        username = callback.from_user.username
        first_name = callback.from_user.first_name
        referrals = 0

    # Sevimli kinolar soni
    favorites = get_favorites_count(user_id)

    # Username bo'lmasa, alohida ko'rsatamiz
    if username:

        username_text = f"@{username}"

    else:

        username_text = "Username mavjud emas"

    text = (
        "👤 <b>MENING PROFILIM</b>\n\n"
        f"👤 Ism: <b>{first_name}</b>\n"
        f"🔗 Username: {username_text}\n"
        f"🆔 ID: <code>{saved_user_id}</code>\n\n"
        "📊 <b>Statistika</b>\n"
        f"❤️ Sevimli kinolar: <b>{favorites}</b>\n"
        f"👥 Taklif qilgan do'stlar: <b>{referrals}</b>\n"
    )

    await callback.message.edit_text(
        text,
        reply_markup=profile_menu()
    )

    await callback.answer()


# ============================================================
# 3. REFERRAL TIZIMI
# ============================================================
#
# Har bir foydalanuvchiga maxsus havola beramiz.
#
# Masalan:
#
# https://t.me/UZKINO_X24_bot?start=123456789
#
# Foydalanuvchi shu havolani do'stiga yuboradi.
#
# Keyinchalik /start ichida bu kodni ushlab,
# referral sonini oshiramiz.
# ============================================================

@router.callback_query(
    F.data == "referral"
)
async def referral_handler(
    callback: CallbackQuery,
    bot
):

    user_id = callback.from_user.id

    # Bot username'ini Telegramdan olamiz
    bot_info = await bot.get_me()

    bot_username = bot_info.username

    # Shaxsiy referral havola
    referral_link = (
        f"https://t.me/{bot_username}?start={user_id}"
    )

    referrals = get_referral_count(user_id)

    text = (
        "🔗 <b>DO'STLARNI TAKLIF QILISH</b>\n\n"
        "Do'stlaringizga quyidagi havolani yuboring:\n\n"
        f"<code>{referral_link}</code>\n\n"
        f"👥 Siz taklif qilganlar: <b>{referrals}</b>\n\n"
        "🎁 Keyinchalik referral tizimiga bonuslar ham "
        "qo'shishimiz mumkin."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📤 Havolani ulashish",
                    url=(
                        "https://t.me/share/url?"
                        f"url={referral_link}"
                    )
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Profil",
                    callback_data="profile"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await callback.answer()


# ============================================================
# 4. YORDAM BO'LIMI
# ============================================================
#
# Foydalanuvchi botdan foydalanishda qiynalsa,
# shu bo'limdan foydalanadi.
# ============================================================

@router.callback_query(
    F.data == "help"
)
async def help_handler(
    callback: CallbackQuery
):

    text = (
        "🆘 <b>YORDAM</b>\n\n"
        "🎬 <b>Kino olish:</b>\n"
        "Kino kodini yuboring.\n\n"
        "🔎 <b>Kino qidirish:</b>\n"
        "«Kino qidirish» tugmasini bosing va "
        "kino nomini yozing.\n\n"
        "❤️ <b>Sevimlilar:</b>\n"
        "Yoqtirgan kinolaringizni saqlab qo'ying.\n\n"
        "📢 <b>Majburiy obuna:</b>\n"
        "Kino olishdan oldin ko'rsatilgan kanallarga "
        "obuna bo'lish kerak.\n\n"
        "❓ Muammo bo'lsa, administrator bilan bog'laning."
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Bosh menyu",
                    callback_data="main_menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )

    await callback.answer()


# ============================================================
# 5. JANRLAR BO'LIMI
# ============================================================
#
# Hozircha janrlar menyusini tayyorlaymiz.
# Keyingi bosqichda bazadagi mavjud janrlarni avtomatik
# chiqaramiz va bosilganda shu janrdagi kinolarni ko'rsatamiz.
# ============================================================

@router.callback_query(
    F.data == "genres"
)
async def genres_handler(
    callback: CallbackQuery
):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="😂 Komediya",
                    callback_data="genre:Komediya"
                ),
                InlineKeyboardButton(
                    text="🎭 Drama",
                    callback_data="genre:Drama"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🔫 Jangari",
                    callback_data="genre:Jangari"
                ),
                InlineKeyboardButton(
                    text="👻 Qo'rqinchli",
                    callback_data="genre:Qo'rqinchli"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🚀 Fantastika",
                    callback_data="genre:Fantastika"
                ),
                InlineKeyboardButton(
                    text="❤️ Romantika",
                    callback_data="genre:Romantika"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🏠 Bosh menyu",
                    callback_data="main_menu"
                )
            ]
        ]
    )

    await callback.message.edit_text(
        "🎭 <b>JANRLAR</b>\n\n"
        "Kerakli janrni tanlang:",
        reply_markup=keyboard
    )

    await callback.answer()


# ============================================================
# 6. FOYDALANUVCHI SONI
# ============================================================
#
# Bu funksiya hozircha kichik yordamchi funksiya.
# Keyinchalik admin statistikasida ishlatamiz.
# ============================================================

def get_total_users():

    return get_users_count()
