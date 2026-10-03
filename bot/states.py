# ============================================================
# UZ KINO BOT
# 3-FAYL: states.py
# ============================================================
#
# FSM — bot foydalanuvchidan ayni paytda nima kutayotganini
# eslab turish uchun ishlatiladi.
#
# Masalan:
#
# Admin "➕ Kino qo'shish" tugmasini bosadi.
# Bot: "Videoni yuboring" deydi.
#
# Shundan keyin yuborilgan video oddiy video emas,
# KINO QO'SHISH uchun yuborilgan video ekanini bot biladi.
#
# Xuddi shunday:
# - kanal qo'shish
# - kino o'chirish
# - reklama yuborish
# - bot nomini o'zgartirish
# va boshqa amallar uchun holatlar yaratiladi.
# ============================================================

from aiogram.fsm.state import State, StatesGroup


# ============================================================
# KINO QO'SHISH HOLATLARI
# ============================================================

class AddMovieState(StatesGroup):

    # Admin videoni yuborishini kutish
    waiting_video = State()

    # Kino ma'lumotlarini kutish
    # Masalan: nomi, janri, yili, sifati
    waiting_info = State()


# ============================================================
# KINO O'CHIRISH HOLATI
# ============================================================

class DeleteMovieState(StatesGroup):

    # Admin kino kodini yuborishini kutish
    waiting_code = State()


# ============================================================
# KINO TAHRIRLASH HOLATI
# ============================================================

class EditMovieState(StatesGroup):

    # Tahrirlanadigan kino kodini kutish
    waiting_code = State()

    # Yangi ma'lumotlarni kutish
    waiting_info = State()


# ============================================================
# KANAL QO'SHISH HOLATI
# ============================================================

class AddChannelState(StatesGroup):

    # Kanal username yoki havolasini kutish
    waiting_channel = State()


# ============================================================
# KANAL O'CHIRISH HOLATI
# ============================================================

class DeleteChannelState(StatesGroup):

    # O'chiriladigan kanalni kutish
    waiting_channel = State()


# ============================================================
# REKLAMA YUBORISH HOLATI
# ============================================================

class BroadcastState(StatesGroup):

    # Admin yuboriladigan xabarni kutish
    waiting_message = State()


# ============================================================
# BOT SOZLAMALARI
# ============================================================

class BotSettingsState(StatesGroup):

    # Bot nomini kutish
    waiting_name = State()

    # Bot description'ini kutish
    waiting_description = State()

    # Bot About qismini kutish
    waiting_about = State()

    # Bot profil rasmini kutish
    waiting_photo = State()


# ============================================================
# KINO QIDIRISH HOLATI
# ============================================================

class SearchMovieState(StatesGroup):

    # Foydalanuvchi kino nomini yozishini kutish
    waiting_query = State()
