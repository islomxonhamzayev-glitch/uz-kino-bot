# ============================================================
# UZ KINO BOT — KINOLAR HANDLERI
# ============================================================

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.states import SearchMovieState

from bot.services.movie_service import (
    get_movies_by_code,
    search_movies_by_title,
    increase_movie_views,
    get_top_movies,
    get_new_movies,
    get_random_movies,
    add_movie,
)

from bot.services.user_service import (
    add_favorite,
    remove_favorite,
    is_favorite,
    get_favorite_movies,
)

from bot.handlers.channels import (
    is_user_subscribed,
    subscription_keyboard,
)

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


# ============================================================
# 1. ROUTER
# ============================================================

router = Router()


# ============================================================
# 2. KINO TUGMALARI
# ============================================================

def movie_buttons(code: str, favorite: bool = False):

    if favorite:
        favorite_text = "💔 Sevimlilardan o'chirish"
    else:
        favorite_text = "❤️ Sevimlilarga qo'shish"

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=favorite_text,
                    callback_data=f"favorite:{code}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Bosh menyu",
                    callback_data="main_menu"
                )
            ]
        ]
    )


# ============================================================
# 3. KINO CAPTIONI
# ============================================================

def movie_caption(
    title,
    genre=None,
    year=None,
    quality=None,
    code=None
):

    text = f"🎬 <b>{title}</b>\n\n"

    if genre:
        text += f"🎭 Janr: <b>{genre}</b>\n"

    if year:
        text += f"📅 Yil: <b>{year}</b>\n"

    if quality:
        text += f"🎥 Sifat: <b>{quality}</b>\n"

    if code:
        text += f"🔢 Kod: <code>{code}</code>\n"

    text += "\n🍿 <i>Yaxshi tomosha!</i>"

    return text


# ============================================================
# 4. OBUNANI TEKSHIRISH
# ============================================================

async def check_subscription(
    message: Message,
    bot: Bot
):

    subscribed = await is_user_subscribed(
        bot,
        message.from_user.id
    )

    if not subscribed:

        await message.answer(
            "🔒 <b>Kino olishdan oldin kanallarga obuna bo'ling.</b>\n\n"
            "📢 Quyidagi kanallarga obuna bo'ling.\n"
            "Keyin <b>✅ Obunani tekshirish</b> tugmasini bosing.",
            reply_markup=subscription_keyboard()
        )

        return False

    return True


# ============================================================
# 5. QIDIRUV TUGMASI
# ============================================================

@router.callback_query(F.data == "search_movie")
async def search_movie(
    callback: CallbackQuery,
    state: FSMContext
):

    await state.set_state(
        SearchMovieState.waiting_query
    )

    await callback.message.answer(
        "🔎 <b>Kino qidirish</b>\n\n"
        "Kino kodini yoki kino nomini yuboring."
    )

    await callback.answer()


# ============================================================
# 6. QIDIRUV REJIMI
# MUHIM: BU HANDLER KOD HANDLERIDAN OLDIN TURADI
# ============================================================

@router.message(SearchMovieState.waiting_query, F.text)
async def search_movie_by_query(
    message: Message,
    state: FSMContext,
    bot: Bot
):

    query = message.text.strip()

    # Qidiruv rejimini tugatamiz
    await state.clear()

    # Obunani tekshiramiz
    subscribed = await is_user_subscribed(
        bot,
        message.from_user.id
    )

    if not subscribed:

        await message.answer(
            "🔒 <b>Kino qidirishdan oldin kanallarga obuna bo'ling.</b>\n\n"
            "📢 Kanallarga obuna bo'ling va tekshirish tugmasini bosing.",
            reply_markup=subscription_keyboard()
        )

        return

    # --------------------------------------------------------
    # Agar raqam bo'lsa — kod bo'yicha qidiramiz
    # --------------------------------------------------------

    if query.isdigit():

        movies = get_movies_by_code(query)

        if not movies:

            await message.answer(
                "❌ <b>Bunday kodli kino topilmadi.</b>\n\n"
                "🔎 Kodni tekshirib qaytadan yuboring."
            )

            return

        await send_movies(message, movies)
        return

    # --------------------------------------------------------
    # Raqam bo'lmasa — nom bo'yicha qidiramiz
    # Topilgan BARCHA mos videolar yuboriladi
    # --------------------------------------------------------

    movies = search_movies_by_title(query)

    if not movies:

        await message.answer(
            "❌ <b>Kino topilmadi.</b>\n\n"
            "Boshqa nom bilan qidirib ko'ring."
        )

        return

    await send_movies(message, movies)


# ============================================================
# 7. KINO YUBORISH — ASOSIY FUNKSIYA
# Barcha mos videolar ketma-ket yuboriladi
# ============================================================

async def send_movie(
    message: Message,
    movie,
    user_id: int | None = None
):
    await send_movies(message, [movie], user_id=user_id)


async def send_movies(
    message: Message,
    movies,
    user_id: int | None = None
):
    if not movies:
        return

    uid = user_id
    if uid is None and message.from_user:
        uid = message.from_user.id

    # Ko'rishlar sonini har bir unikal kod uchun bir marta oshiramiz
    seen_codes = set()

    total = len(movies)

    for index, movie in enumerate(movies, start=1):

        (
            movie_code,
            file_id,
            title,
            genre,
            year,
            quality,
            views,
            added_at
        ) = movie

        if movie_code not in seen_codes:
            increase_movie_views(movie_code)
            seen_codes.add(movie_code)

        favorite = False
        if uid is not None:
            favorite = is_favorite(uid, movie_code)

        caption = movie_caption(
            title,
            genre,
            year,
            quality,
            movie_code
        )

        if total > 1:
            caption = (
                f"📦 <b>{index}/{total}</b>\n\n"
                + caption
            )

        # Oxirgi videoda sevimli tugmalari
        reply_markup = None
        if index == total and uid is not None:
            reply_markup = movie_buttons(
                movie_code,
                favorite
            )

        try:
            await message.answer_video(
                video=file_id,
                caption=caption,
                reply_markup=reply_markup
            )
        except Exception:
            # Ba'zi file_id lar document sifatida saqlangan bo'lishi mumkin
            await message.answer_document(
                document=file_id,
                caption=caption,
                reply_markup=reply_markup
            )


# ============================================================
# 8. ODDIY KINO KODI
# MUHIM: SEARCH STATE HANDLERIDAN KEYIN TURIBDI
# ============================================================

@router.message(F.text.regexp(r"^\d+$"))
async def search_movie_by_code(
    message: Message,
    bot: Bot
):

    code = message.text.strip()

    # Bazadan shu kodli BARCHA videolarni olamiz
    movies = get_movies_by_code(code)

    if not movies:

        await message.answer(
            "❌ <b>Bunday kodli kino topilmadi.</b>\n\n"
            "🔎 Kodni tekshirib qaytadan yuboring."
        )

        return

    # Majburiy obuna
    subscribed = await check_subscription(
        message,
        bot
    )

    if not subscribed:
        return

    await send_movies(message, movies)


# ============================================================
# 9. QIDIRUV NATIJASIDAN KINO TANLASH
# ============================================================

@router.callback_query(F.data.startswith("movie:"))
async def selected_movie(
    callback: CallbackQuery,
    bot: Bot
):

    code = callback.data.split(":", 1)[1]

    subscribed = await is_user_subscribed(
        bot,
        callback.from_user.id
    )

    if not subscribed:

        await callback.message.answer(
            "🔒 <b>Kino olishdan oldin kanallarga obuna bo'ling.</b>",
            reply_markup=subscription_keyboard()
        )

        await callback.answer()

        return

    movie = get_movies_by_code(code)

    if not movie:

        await callback.answer(
            "❌ Kino topilmadi.",
            show_alert=True
        )

        return

    await send_movies(
        callback.message,
        movie,
        user_id=callback.from_user.id
    )

    await callback.answer()


# ============================================================
# 10. TOP KINOLAR
# ============================================================

@router.callback_query(F.data == "top_movies")
async def top_movies(
    callback: CallbackQuery,
    bot: Bot
):

    subscribed = await is_user_subscribed(
        bot,
        callback.from_user.id
    )

    if not subscribed:

        await callback.message.answer(
            "🔒 <b>Avval kanallarga obuna bo'ling.</b>",
            reply_markup=subscription_keyboard()
        )

        await callback.answer()

        return

    movies = get_top_movies(10)

    if not movies:

        await callback.message.answer(
            "📭 Hozircha kinolar mavjud emas."
        )

        await callback.answer()

        return

    buttons = []

    for index, movie in enumerate(movies, start=1):

        code = movie[0]
        title = movie[2]
        views = movie[6] or 0

        buttons.append([
            InlineKeyboardButton(
                text=f"🔥 {index}. {title} — {views} ta",
                callback_data=f"movie:{code}"
            )
        ])

    await callback.message.answer(
        "🔥 <b>TOP KINOLAR</b>\n\n"
        "Eng ko'p ko'rilgan kinolar:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )

    await callback.answer()


# ============================================================
# 11. YANGI KINOLAR
# ============================================================

@router.callback_query(F.data == "new_movies")
async def new_movies(
    callback: CallbackQuery,
    bot: Bot
):

    subscribed = await is_user_subscribed(
        bot,
        callback.from_user.id
    )

    if not subscribed:

        await callback.message.answer(
            "🔒 <b>Avval kanallarga obuna bo'ling.</b>",
            reply_markup=subscription_keyboard()
        )

        await callback.answer()

        return

    movies = get_new_movies(10)

    if not movies:

        await callback.message.answer(
            "📭 Hozircha yangi kinolar yo'q."
        )

        await callback.answer()

        return

    buttons = []

    for movie in movies:

        code = movie[0]
        title = movie[2]

        buttons.append([
            InlineKeyboardButton(
                text=f"🆕 {title}",
                callback_data=f"movie:{code}"
            )
        ])

    await callback.message.answer(
        "🆕 <b>YANGI KINOLAR</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )

    await callback.answer()


# ============================================================
# 12. RANDOM KINO
# ============================================================

@router.callback_query(F.data == "random_movie")
async def random_movie(
    callback: CallbackQuery,
    bot: Bot
):

    subscribed = await is_user_subscribed(
        bot,
        callback.from_user.id
    )

    if not subscribed:

        await callback.message.answer(
            "🔒 <b>Avval kanallarga obuna bo'ling.</b>",
            reply_markup=subscription_keyboard()
        )

        await callback.answer()

        return

    movies = get_random_movies()

    if not movies:

        await callback.message.answer(
            "📭 Hozircha kinolar mavjud emas."
        )

        await callback.answer()

        return

    await send_movies(
        callback.message,
        movies,
        user_id=callback.from_user.id
    )

    await callback.answer()


# ============================================================
# 13. SEVIMLIGA QO'SHISH / O'CHIRISH
# ============================================================

@router.callback_query(F.data.startswith("favorite:"))
async def favorite_movie(
    callback: CallbackQuery
):

    code = callback.data.split(":", 1)[1]

    user_id = callback.from_user.id

    favorite = is_favorite(
        user_id,
        code
    )

    if favorite:

        remove_favorite(
            user_id,
            code
        )

        await callback.answer(
            "💔 Sevimlilardan o'chirildi."
        )

    else:

        add_favorite(
            user_id,
            code
        )

        await callback.answer(
            "❤️ Sevimlilarga qo'shildi!"
        )


# ============================================================
# 14. SEVIMLILAR
# ============================================================

@router.callback_query(F.data == "favorites")
async def favorites(
    callback: CallbackQuery,
    bot: Bot
):

    subscribed = await is_user_subscribed(
        bot,
        callback.from_user.id
    )

    if not subscribed:

        await callback.message.answer(
            "🔒 <b>Avval kanallarga obuna bo'ling.</b>",
            reply_markup=subscription_keyboard()
        )

        await callback.answer()

        return

    movies = get_favorite_movies(
        callback.from_user.id
    )

    if not movies:

        await callback.message.answer(
            "❤️ <b>Sevimlilar</b>\n\n"
            "Hozircha sevimli kino qo'shilmagan."
        )

        await callback.answer()

        return

    buttons = []

    for movie in movies:

        # get_favorite_movies: (code, title, genre, year, quality)
        code = movie[0]
        title = movie[1]

        buttons.append([
            InlineKeyboardButton(
                text=f"❤️ {title}",
                callback_data=f"movie:{code}"
            )
        ])

    await callback.message.answer(
        "❤️ <b>SEVIMLI KINOLAR</b>",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=buttons
        )
    )

    await callback.answer()


# ============================================================
# 15. KINO BAZA GURUHIDAN AVTOMATIK SAQLASH
# ============================================================

import asyncio
import re
from collections import defaultdict


CODE_PATTERN = re.compile(
    r"(?:kino\s*kodi|kod|code|#)\s*[:\-–]?\s*(\d+)",
    re.IGNORECASE,
)

# Media group (albom) uchun vaqtinchalik bufer:
# bir xabar caption bilan, qolganlari caption'siz kelishi mumkin.
_media_group_buffer = defaultdict(lambda: {
    "caption": None,
    "file_ids": [],
    "task": None,
})
_media_group_lock = None


def _get_media_group_lock():
    global _media_group_lock
    if _media_group_lock is None:
        _media_group_lock = asyncio.Lock()
    return _media_group_lock


def extract_video_file_id(message: Message):
    """Video yoki video-document dan file_id olish."""

    if message.video:
        return message.video.file_id

    document = message.document
    if not document:
        return None

    mime = (document.mime_type or "").lower()
    if mime.startswith("video/") or (
        document.file_name
        and document.file_name.lower().endswith(
            (".mp4", ".mkv", ".avi", ".mov", ".webm")
        )
    ):
        return document.file_id

    return None


def parse_movie_caption(caption: str):
    """
    Caption dan kod va nomni ajratib oladi.
    Masalan:
      Kino kodi: 151
      Kod: 123
      #149
    """

    if not caption:
        return None, None

    caption = caption.strip()
    code_match = CODE_PATTERN.search(caption)

    if not code_match:
        return None, None

    code = code_match.group(1).strip()
    title = "Nomsiz kino"

    for line in caption.splitlines():
        line = line.strip()

        if not line:
            continue

        if CODE_PATTERN.search(line):
            continue

        title = line[:200]
        break

    return code, title


async def _flush_media_group(media_group_id: str):
    """Albomdagi barcha videolarni bitta caption bilan saqlaydi."""

    try:
        await asyncio.sleep(1.5)
    except asyncio.CancelledError:
        return

    async with _get_media_group_lock():
        data = _media_group_buffer.pop(media_group_id, None)

    if not data:
        return

    caption = data.get("caption")
    file_ids = data.get("file_ids") or []

    if not caption or not file_ids:
        return

    code, title = parse_movie_caption(caption)

    if not code:
        return

    for file_id in file_ids:
        add_movie(
            code=code,
            file_id=file_id,
            title=title
        )


async def process_source_movie(message: Message):
    """
    Bot admin/a'zo bo'lgan guruh yoki kanaldan kelgan
    videoni bazaga avtomatik qo'shadi.

    - Bir kodga bir nechta video saqlanadi (overwrite yo'q)
    - Media group (albom) qismlari ham saqlanadi
    - Video document lar ham qabul qilinadi
    """

    file_id = extract_video_file_id(message)

    if not file_id:
        return

    media_group_id = message.media_group_id

    # --------------------------------------------------------
    # MEDIA GROUP (albom): caption faqat birinchi postda bo'ladi
    # --------------------------------------------------------

    if media_group_id:
        async with _get_media_group_lock():
            bucket = _media_group_buffer[media_group_id]

            if message.caption:
                bucket["caption"] = message.caption

            if file_id not in bucket["file_ids"]:
                bucket["file_ids"].append(file_id)

            # Oldingi flush vazifasini bekor qilib, yangisini rejalaymiz
            old_task = bucket.get("task")
            if old_task and not old_task.done():
                old_task.cancel()

            bucket["task"] = asyncio.create_task(
                _flush_media_group(media_group_id)
            )

        return

    # --------------------------------------------------------
    # ODDIY POST
    # --------------------------------------------------------

    if not message.caption:
        return

    code, title = parse_movie_caption(message.caption)

    if not code:
        return

    add_movie(
        code=code,
        file_id=file_id,
        title=title
    )

    try:
        await message.reply(
            f"✅ Kino bazaga qo'shildi!\n\n"
            f"🎬 {title}\n"
            f"🔢 Kod: <code>{code}</code>"
        )
    except Exception:
        pass


# ============================================================
# GURUH / SUPERGURUH
# ============================================================

@router.message(
    F.chat.type.in_({"group", "supergroup"}),
    F.video | F.document
)
async def save_movie_from_group(message: Message):
    """
    Bot admin bo'lgan guruh va superguruhdagi
    yangi kino videolarini ushlaydi.
    """

    if not extract_video_file_id(message):
        return

    await process_source_movie(message)


# ============================================================
# KANAL — barcha kanallardagi postlar
# ============================================================

@router.channel_post(F.video | F.document)
async def save_movie_from_channel(message: Message):
    """
    Bot a'zo/admin bo'lgan HAR QANDAY kanaldagi yangi
    kino postlarini ushlaydi va bazaga saqlaydi.
    """

    if not extract_video_file_id(message):
        return

    await process_source_movie(message)
