# ============================================================
# UZ KINO BOT
# 2-FAYL: database.py
# ============================================================
#
# Bu fayl botning MA'LUMOTLAR BAZASI bilan ishlaydi.
#
# SQLite ishlatyapmiz.
#
# Bazada quyidagi asosiy ma'lumotlar bo'ladi:
#
# 1. users     -> foydalanuvchilar
# 2. movies    -> kinolar (bir kodda bir nechta video bo'lishi mumkin)
# 3. channels  -> majburiy obuna kanallari
# 4. favorites -> foydalanuvchining sevimli kinolari
#
# Keyinchalik statistika va referral tizimini ham shu baza
# orqali boshqaramiz.
# ============================================================

import sqlite3

from bot.config import DATABASE_NAME


# ============================================================
# DATABASE ULANISHI
# ============================================================
#
# Har safar kerak bo'lganda SQLite bazasiga ulanish uchun
# alohida funksiya yaratdik.
#
# Buning foydasi:
#   boshqa fayllardan ham shu funksiyani chaqira olamiz.
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ============================================================
# JADVALLARNI YARATISH / MIGRATSIYA
# ============================================================
#
# Bot birinchi marta ishga tushganda kerakli jadvallar
# avtomatik yaratiladi.
#
# movies jadvali: bir kodga bir nechta video (file_id)
# saqlanishi uchun PRIMARY KEY = id, UNIQUE(code, file_id).
# ============================================================

def _movies_needs_migration(cursor):
    """Eski sxema: code PRIMARY KEY va bitta file_id."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='movies'"
    )
    if not cursor.fetchone():
        return False

    cursor.execute("PRAGMA table_info(movies)")
    columns = {row[1]: row for row in cursor.fetchall()}

    if "id" not in columns:
        return True

    # code hali ham PRIMARY KEY bo'lsa (eski sxema)
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='movies'")
    sql = (cursor.fetchone() or [""])[0] or ""
    if "code TEXT PRIMARY KEY" in sql or "code INTEGER PRIMARY KEY" in sql:
        return True

    return False


def _migrate_movies_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT NOT NULL,
            file_id TEXT NOT NULL,
            title TEXT NOT NULL DEFAULT 'Nomsiz kino',
            genre TEXT,
            year INTEGER,
            quality TEXT,
            views INTEGER DEFAULT 0,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(code, file_id)
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO movies_new
            (code, file_id, title, genre, year, quality, views, added_at)
        SELECT
            code,
            file_id,
            COALESCE(title, 'Nomsiz kino'),
            genre,
            year,
            quality,
            COALESCE(views, 0),
            COALESCE(added_at, CURRENT_TIMESTAMP)
        FROM movies
    """)

    cursor.execute("DROP TABLE movies")
    cursor.execute("ALTER TABLE movies_new RENAME TO movies")
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_movies_code ON movies(code)"
    )


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # FOYDALANUVCHILAR JADVALI
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            referrals INTEGER DEFAULT 0
        )
    """)

    # --------------------------------------------------------
    # KINOLAR JADVALI
    # --------------------------------------------------------
    #
    # id          -> avto-increment (har bir video uchun)
    # code        -> kino kodi (bir kodda ko'p video)
    # file_id     -> Telegramdagi video ID
    # title       -> kino nomi
    # genre       -> janri
    # year        -> chiqarilgan yili
    # quality     -> video sifati
    # views       -> necha marta yuborilgani
    # --------------------------------------------------------

    if _movies_needs_migration(cursor):
        _migrate_movies_table(cursor)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                file_id TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT 'Nomsiz kino',
                genre TEXT,
                year INTEGER,
                quality TEXT,
                views INTEGER DEFAULT 0,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(code, file_id)
            )
        """)
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_movies_code ON movies(code)"
        )

    # --------------------------------------------------------
    # MAJBURIY OBUNA KANALLARI
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            username TEXT,
            title TEXT,
            invite_link TEXT
        )
    """)

    # --------------------------------------------------------
    # SEVIMLI KINOLAR
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_code TEXT NOT NULL,
            UNIQUE(user_id, movie_code)
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# FOYDALANUVCHINI SAQLASH
# ============================================================

def save_user(user_id, username, first_name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (
            user_id,
            username,
            first_name
        )
        VALUES (?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name
    """, (
        user_id,
        username,
        first_name
    ))

    connection.commit()
    connection.close()


# ============================================================
# FOYDALANUVCHILAR SONINI OLISH
# ============================================================

def get_users_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users"
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# KINOLAR SONINI OLISH (unikal kodlar)
# ============================================================

def get_movies_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(DISTINCT code) FROM movies"
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# KANALLAR SONINI OLISH
# ============================================================

def get_channels_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM channels"
    )

    count = cursor.fetchone()[0]

    connection.close()

    return count
