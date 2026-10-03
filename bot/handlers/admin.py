# ============================================================
# UZ KINO BOT
# 12-FAYL: handlers/admin.py
# ============================================================
#
# Bu fayl BOTNING ADMIN PANELI hisoblanadi.
#
# Faqat ADMIN_ID egasi bu bo'limlardan foydalana oladi.
#
# Admin bu yerdan:
#
# 🎬 Kinolarni boshqaradi
# 📢 Kanallarni boshqaradi
# 👥 Foydalanuvchilarni ko'radi
# 📊 Statistikani ko'radi
# 📢 Reklama yuboradi
#
# ============================================================


from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from bot.config import ADMIN_ID

from bot.states import (
    AddMovieState,
    DeleteMovieState,
    EditMovieState,
    AddChannelState,
    DeleteChannelState,
    BroadcastState
)

from bot.database import get_connection

from bot.keyboards import (
    admin_menu,
    admin_movies_menu,
    admin_channels_menu
)

from bot.services.movie_service import (
    add_movie,
    delete_movie,
    update_movie,
    get_movie_by_code,
    get_movies_page
)

from bot.services.user_service import (
    get_users_count,
    get_all_users
)

from bot.services.broadcast import (
    broadcast_message,
    format_broadcast_result
)


# ============================================================
# ROUTER
# ============================================================

router = Router()


# ============================================================
# ADMINNI TEKSHIRISH
# ============================================================
#
# Har bir admin funksiyasining boshida shu tekshiruvdan
# foydalanamiz.
#
# Agar Telegram ID ADMIN_ID ga teng bo'lmasa:
# admin panel ishlamaydi.
# ============================================================

def is_admin(user_id: int):

    return user_id == ADMIN_ID


# ============================================================
# 1. ADMIN PANEL
# ============================================================

@router.message(F.text == "/admin")
async def admin_panel(message: Message):

    # Admin emasmi?
    if not is_admin(message.from_user.id):

        await message.answer(
            "❌ Sizda admin huquqi mavjud emas."
        )

        return

    await message.answer(
        "👨‍💼 <b>ADMIN PANEL</b>\n\n"
        "Botning barcha boshqaruv bo'limlari quyida:",
        reply_markup=admin_menu()
    )


# ============================================================
# 2. KINO BOSHQARUVI
# ============================================================

@router.callback_query(
    F.data == "admin_movies"
)
async def admin_movies(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "🎬 <b>KINO BOSHQARUVI</b>\n\n"
        "Kerakli amalni tanlang:",
        reply_markup=admin_movies_menu()
    )

    await callback.answer()


# ============================================================
# 3. KINO QO'SHISH
# ============================================================
#
# Admin "➕ Kino qo'shish" tugmasini bosadi.
# Bot undan videoni kutadi.
# ============================================================

@router.callback_query(
    F.data == "add_movie"
)
async def add_movie_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        AddMovieState.waiting_video
    )

    await callback.message.answer(
        "➕ <b>KINO QO'SHISH</b>\n\n"
        "🎬 Endi kino videosini yuboring.\n\n"
        "Videoni yuborgandan keyin bot sizdan "
        "kino ma'lumotlarini so'raydi."
    )

    await callback.answer()


# ============================================================
# 4. ADMIN VIDEOSINI QABUL QILISH
# ============================================================

@router.message(
    AddMovieState.waiting_video,
    F.video
)
async def receive_movie_video(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    # Telegramdagi videoning file_id sini saqlab olamiz
    file_id = message.video.file_id

    # Keyingi bosqichda shu file_id kerak bo'ladi
    await state.update_data(
        file_id=file_id
    )

    # Endi kino ma'lumotlarini kutamiz
    await state.set_state(
        AddMovieState.waiting_info
    )

    await message.answer(
        "✅ Video qabul qilindi!\n\n"
        "Endi kino ma'lumotlarini quyidagi ko'rinishda yuboring:\n\n"
        "<code>KOD | NOMI | JANR | YIL | SIFAT</code>\n\n"
        "Masalan:\n"
        "<code>123 | Avatar 2 | Fantastika | 2022 | 1080p</code>"
    )


# ============================================================
# 5. KINO MA'LUMOTLARINI SAQLASH
# ============================================================

@router.message(
    AddMovieState.waiting_info,
    F.text
)
async def receive_movie_info(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    text = message.text.strip()

    # "|" belgisi bo'yicha bo'lamiz
    parts = [
        item.strip()
        for item in text.split("|")
    ]

    # 5 ta ma'lumot bo'lishi kerak
    if len(parts) != 5:

        await message.answer(
            "❌ Format noto'g'ri.\n\n"
            "To'g'ri ko'rinish:\n\n"
            "<code>KOD | NOMI | JANR | YIL | SIFAT</code>\n\n"
            "Masalan:\n"
            "<code>123 | Avatar 2 | Fantastika | 2022 | 1080p</code>"
        )

        return

    code = parts[0]
    title = parts[1]
    genre = parts[2]
    year_text = parts[3]
    quality = parts[4]

    # Yilni raqamga aylantiramiz
    try:

        year = int(year_text)

    except ValueError:

        await message.answer(
            "❌ Yil faqat raqam bo'lishi kerak.\n\n"
            "Masalan: <code>2022</code>"
        )

        return

    # Oldingi bosqichda saqlangan video file_id
    data = await state.get_data()

    file_id = data.get("file_id")

    if not file_id:

        await message.answer(
            "❌ Video ma'lumoti topilmadi. "
            "Kino qo'shishni qaytadan boshlang."
        )

        await state.clear()

        return

    # Bazaga kino qo'shamiz
    add_movie(
        code=code,
        file_id=file_id,
        title=title,
        genre=genre,
        year=year,
        quality=quality
    )

    # Holatni tozalaymiz
    await state.clear()

    await message.answer(
        "✅ <b>KINO MUVAFFAQIYATLI SAQLANDI!</b>\n\n"
        f"🔢 Kod: <code>{code}</code>\n"
        f"🎬 Nomi: <b>{title}</b>\n"
        f"🎭 Janr: {genre}\n"
        f"📅 Yil: {year}\n"
        f"🎞 Sifat: {quality}"
    )


# ============================================================
# 6. KINO O'CHIRISH
# ============================================================

@router.callback_query(
    F.data == "delete_movie"
)
async def delete_movie_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        DeleteMovieState.waiting_code
    )

    await callback.message.answer(
        "🗑 <b>KINO O'CHIRISH</b>\n\n"
        "O'chiriladigan kino kodini yuboring.\n\n"
        "Masalan:\n"
        "<code>123</code>"
    )

    await callback.answer()


@router.message(
    DeleteMovieState.waiting_code
)
async def delete_movie_handler(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    code = message.text.strip()

    deleted = delete_movie(code)

    await state.clear()

    if deleted:

        await message.answer(
            f"✅ <b>Kino o'chirildi.</b>\n\n"
            f"🔢 Kod: <code>{code}</code>"
        )

    else:

        await message.answer(
            "❌ Bunday kodli kino topilmadi."
        )


# ============================================================
# 7. KINO TAHRIRLASH
# ============================================================

@router.callback_query(
    F.data == "edit_movie"
)
async def edit_movie_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        EditMovieState.waiting_code
    )

    await callback.message.answer(
        "✏️ <b>KINO TAHRIRLASH</b>\n\n"
        "Tahrirlanadigan kino kodini yuboring."
    )

    await callback.answer()


@router.message(
    EditMovieState.waiting_code
)
async def edit_movie_code(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    code = message.text.strip()

    movie = get_movie_by_code(code)

    if not movie:

        await message.answer(
            "❌ Bunday kino topilmadi."
        )

        return

    # Kodni keyingi holatga saqlaymiz
    await state.update_data(
        code=code
    )

    await state.set_state(
        EditMovieState.waiting_info
    )

    await message.answer(
        "✏️ Yangi ma'lumotlarni yuboring:\n\n"
        "<code>NOMI | JANR | YIL | SIFAT</code>\n\n"
        "Masalan:\n"
        "<code>Avatar 2 | Fantastika | 2022 | 1080p</code>"
    )


@router.message(
    EditMovieState.waiting_info,
    F.text
)
async def edit_movie_info(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    parts = [
        item.strip()
        for item in message.text.split("|")
    ]

    if len(parts) != 4:

        await message.answer(
            "❌ Format noto'g'ri.\n\n"
            "<code>NOMI | JANR | YIL | SIFAT</code>"
        )

        return

    title = parts[0]
    genre = parts[1]
    year_text = parts[2]
    quality = parts[3]

    try:

        year = int(year_text)

    except ValueError:

        await message.answer(
            "❌ Yil raqam bo'lishi kerak."
        )

        return

    data = await state.get_data()

    code = data.get("code")

    updated = update_movie(
        code=code,
        title=title,
        genre=genre,
        year=year,
        quality=quality
    )

    await state.clear()

    if updated:

        await message.answer(
            "✅ <b>Kino yangilandi!</b>\n\n"
            f"🔢 Kod: <code>{code}</code>\n"
            f"🎬 Nomi: {title}\n"
            f"🎭 Janr: {genre}\n"
            f"📅 Yil: {year}\n"
            f"🎞 Sifat: {quality}"
        )

    else:

        await message.answer(
            "❌ Kino yangilanmadi."
        )


# ============================================================
# 8. KINOLAR RO'YXATI
# ============================================================

@router.callback_query(
    F.data == "movie_list"
)
async def movie_list(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    movies = get_movies_page(
        page=1,
        per_page=15
    )

    if not movies:

        await callback.message.answer(
            "🎬 Bazada hali kino yo'q."
        )

        await callback.answer()

        return

    text = "📋 <b>OXIRGI KINOLAR</b>\n\n"

    for movie in movies:

        # (code, file_id, title, genre, year, quality, views, added_at)
        code = movie[0]
        title = movie[2]
        year = movie[4]
        views = movie[6]

        text += (
            f"🎬 <b>{title}</b>\n"
            f"🔢 Kod: <code>{code}</code>\n"
            f"📅 {year or '-'} | 👁 {views}\n\n"
        )

    await callback.message.answer(text)

    await callback.answer()


# ============================================================
# 9. KANAL BOSHQARUVI
# ============================================================

@router.callback_query(
    F.data == "admin_channels"
)
async def admin_channels(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "📢 <b>KANAL BOSHQARUVI</b>\n\n"
        "Kerakli amalni tanlang:",
        reply_markup=admin_channels_menu()
    )

    await callback.answer()


# ============================================================
# 10. KANAL QO'SHISH
# ============================================================

@router.callback_query(
    F.data == "add_channel"
)
async def add_channel_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        AddChannelState.waiting_channel
    )

    await callback.message.answer(
        "📢 <b>KANAL QO'SHISH</b>\n\n"
        "Kanal username'ini yuboring.\n\n"
        "Masalan:\n"
        "<code>@uzkino</code>\n\n"
        "⚠️ Bot kanalga administrator qilib qo'yilgan "
        "bo'lishi kerak."
    )

    await callback.answer()


# ============================================================
# 11. KANALNI BAZAGA SAQLASH
# ============================================================

@router.message(
    AddChannelState.waiting_channel,
    F.text
)
async def add_channel_handler(
    message: Message,
    state: FSMContext,
    bot
):

    if not is_admin(message.from_user.id):
        return

    username = message.text.strip()

    if not username.startswith("@"):

        await message.answer(
            "❌ Kanal username'i @ bilan boshlanishi kerak.\n\n"
            "Masalan: <code>@uzkino</code>"
        )

        return

    try:

        # Telegramdan kanal ma'lumotlarini olamiz
        chat = await bot.get_chat(username)

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO channels (
                chat_id,
                username,
                title,
                invite_link
            )
            VALUES (?, ?, ?, ?)
        """, (
            chat.id,
            username,
            chat.title or username,
            None
        ))

        connection.commit()
        connection.close()

        await state.clear()

        await message.answer(
            "✅ <b>KANAL QO'SHILDI!</b>\n\n"
            f"📢 {chat.title}\n"
            f"🔗 {username}"
        )

    except Exception:

        await message.answer(
            "❌ Kanalni qo'shib bo'lmadi.\n\n"
            "Tekshiring:\n"
            "• Username to'g'ri yozilganmi?\n"
            "• Bot kanalga adminmi?"
        )


# ============================================================
# 12. KANALLAR RO'YXATI
# ============================================================

@router.callback_query(
    F.data == "channel_list"
)
async def channel_list(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            username
        FROM channels
        ORDER BY id ASC
    """)

    channels = cursor.fetchall()

    connection.close()

    if not channels:

        await callback.message.answer(
            "📢 Hozircha kanal qo'shilmagan."
        )

        await callback.answer()

        return

    text = "📢 <b>MAJBURIY KANALLAR</b>\n\n"

    for channel in channels:

        channel_id = channel[0]
        title = channel[1]
        username = channel[2]

        text += (
            f"#{channel_id} — <b>{title}</b>\n"
            f"🔗 {username}\n\n"
        )

    await callback.message.answer(text)

    await callback.answer()


# ============================================================
# 13. KANAL O'CHIRISH
# ============================================================

@router.callback_query(
    F.data == "delete_channel"
)
async def delete_channel_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        DeleteChannelState.waiting_channel
    )

    await callback.message.answer(
        "🗑 <b>KANAL O'CHIRISH</b>\n\n"
        "O'chiriladigan kanal username'ini yuboring.\n\n"
        "Masalan:\n"
        "<code>@uzkino</code>"
    )

    await callback.answer()


@router.message(
    DeleteChannelState.waiting_channel
)
async def delete_channel_handler(
    message: Message,
    state: FSMContext
):

    if not is_admin(message.from_user.id):
        return

    username = message.text.strip()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM channels
        WHERE username = ?
    """, (username,))

    deleted = cursor.rowcount

    connection.commit()
    connection.close()

    await state.clear()

    if deleted:

        await message.answer(
            f"✅ {username} kanali o'chirildi."
        )

    else:

        await message.answer(
            "❌ Bunday kanal topilmadi."
        )


# ============================================================
# 14. STATISTIKA
# ============================================================

@router.callback_query(
    F.data == "statistics"
)
async def statistics(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    connection = get_connection()
    cursor = connection.cursor()

    # Foydalanuvchilar
    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )
    users = cursor.fetchone()[0]

    # Kinolar (unikal kodlar)
    cursor.execute(
        "SELECT COUNT(DISTINCT code) FROM movies"
    )
    movies = cursor.fetchone()[0]

    # Kanallar
    cursor.execute(
        "SELECT COUNT(*) FROM channels"
    )
    channels = cursor.fetchone()[0]

    # Barcha kino ko'rishlari (har kod bir marta)
    cursor.execute("""
        SELECT COALESCE(SUM(v), 0) FROM (
            SELECT MAX(views) AS v
            FROM movies
            GROUP BY code
        )
    """)
    views = cursor.fetchone()[0]

    connection.close()

    text = (
        "📊 <b>BOT STATISTIKASI</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b>\n"
        f"🎬 Kinolar: <b>{movies}</b>\n"
        f"📢 Kanallar: <b>{channels}</b>\n"
        f"👁 Kino ko'rishlar: <b>{views}</b>"
    )

    await callback.message.answer(text)

    await callback.answer()


# ============================================================
# 15. FOYDALANUVCHILAR
# ============================================================

@router.callback_query(
    F.data == "admin_users"
)
async def admin_users(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    count = get_users_count()

    await callback.message.answer(
        "👥 <b>FOYDALANUVCHILAR</b>\n\n"
        f"👤 Jami foydalanuvchilar: <b>{count}</b>"
    )

    await callback.answer()


# ============================================================
# 16. REKLAMA BOSHLASH
# ============================================================

@router.callback_query(
    F.data == "broadcast"
)
async def broadcast_start(
    callback: CallbackQuery,
    state: FSMContext
):

    if not is_admin(callback.from_user.id):
        return

    await state.set_state(
        BroadcastState.waiting_message
    )

    await callback.message.answer(
        "📢 <b>REKLAMA YUBORISH</b>\n\n"
        "Endi foydalanuvchilarga yubormoqchi bo'lgan "
        "xabaringizni shu yerga yuboring.\n\n"
        "Matn, rasm, video yoki boshqa Telegram xabar "
        "bo'lishi mumkin."
    )

    await callback.answer()


# ============================================================
# 17. REKLAMANI BARCHAGA YUBORISH
# ============================================================

@router.message(
    BroadcastState.waiting_message
)
async def broadcast_handler(
    message: Message,
    state: FSMContext,
    bot
):

    if not is_admin(message.from_user.id):
        return

    # Xabarni barcha foydalanuvchilarga yuboramiz
    result = await broadcast_message(
        bot=bot,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )

    await state.clear()

    # Natijani chiroyli qilib chiqaramiz
    text = format_broadcast_result(result)

    await message.answer(
        text
    )


# ============================================================
# 18. ADMIN PANELGA QAYTISH
# ============================================================

@router.callback_query(
    F.data == "back_admin"
)
async def back_admin(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.edit_text(
        "👨‍💼 <b>ADMIN PANEL</b>\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=admin_menu()
    )

    await callback.answer()


# ============================================================
# 19. ADMIN PANELNI YOPISH
# ============================================================

@router.callback_query(
    F.data == "close_admin"
)
async def close_admin(
    callback: CallbackQuery
):

    if not is_admin(callback.from_user.id):
        return

    await callback.message.delete()

    await callback.answer(
        "Admin panel yopildi."
    )
    
