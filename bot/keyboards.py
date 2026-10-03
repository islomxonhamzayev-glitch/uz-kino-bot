# ============================================================
# UZ KINO BOT — KEYBOARDS
# Foydalanuvchi va admin uchun barcha tugmalar shu yerda.
# ============================================================

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


# ============================================================
# 1. FOYDALANUVCHI ASOSIY MENYUSI
# ============================================================

def main_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔎 Kino qidirish",
                    callback_data="search_movie"
                ),
                InlineKeyboardButton(
                    text="🔥 Top kinolar",
                    callback_data="top_movies"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🆕 Yangi kinolar",
                    callback_data="new_movies"
                ),
                InlineKeyboardButton(
                    text="🎲 Random kino",
                    callback_data="random_movie"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎭 Janrlar",
                    callback_data="genres"
                ),
                InlineKeyboardButton(
                    text="❤️ Sevimlilar",
                    callback_data="favorites"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👤 Profil",
                    callback_data="profile"
                ),
                InlineKeyboardButton(
                    text="🆘 Yordam",
                    callback_data="help"
                )
            ]
        ]
    )


# ============================================================
# 2. ADMIN ASOSIY MENYUSI
# ============================================================

def admin_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎬 Kino boshqaruvi",
                    callback_data="admin_movies"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Kanal boshqaruvi",
                    callback_data="admin_channels"
                )
            ],
            [
                InlineKeyboardButton(
                    text="👥 Foydalanuvchilar",
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Statistika",
                    callback_data="statistics"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Reklama yuborish",
                    callback_data="broadcast"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Bot sozlamalari",
                    callback_data="bot_settings"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Yopish",
                    callback_data="close_admin"
                )
            ]
        ]
    )


# ============================================================
# 3. KINO BOSHQARUVI
# ============================================================

def admin_movies_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Kino qo'shish",
                    callback_data="add_movie"
                )
            ],
            [
                InlineKeyboardButton(
                    text="✏️ Kino tahrirlash",
                    callback_data="edit_movie"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Kino o'chirish",
                    callback_data="delete_movie"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔎 Kino qidirish",
                    callback_data="admin_search_movie"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Kino ro'yxati",
                    callback_data="movie_list"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back_admin"
                )
            ]
        ]
    )


# ============================================================
# 4. KANAL BOSHQARUVI
# ============================================================

def admin_channels_menu():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Kanal qo'shish",
                    callback_data="add_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 Kanal o'chirish",
                    callback_data="delete_channel"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Kanallar ro'yxati",
                    callback_data="channel_list"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back_admin"
                )
            ]
        ]
    )


# ============================================================
# 5. BOT SOZLAMALARI
# ============================================================

def bot_settings_menu():

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
                    text="📝 Bot tavsifi",
                    callback_data="bot_description"
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Bot haqida",
                    callback_data="bot_about"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🖼 Bot rasmi",
                    callback_data="bot_photo"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data="back_admin"
                )
            ]
        ]
    )


# ============================================================
# 6. ORQAGA TUGMASI
# ============================================================

def back_button(callback_data="back_admin"):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Orqaga",
                    callback_data=callback_data
                )
            ]
        ]
    )
