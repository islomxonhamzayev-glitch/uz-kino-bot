# ============================================================
# UZ KINO BOT — MOVIE SERVICE
# Kinolar bazasi bilan ishlaydigan barcha funksiyalar.
# ============================================================

import sqlite3

from bot.config import DATABASE_NAME


# ============================================================
# 1. DATABASE ULANISH
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ============================================================
# 2. KINO QO'SHISH
# ============================================================
#
# Bir xil kodga bir nechta video qo'shilishi mumkin.
# Faqat bir xil (code, file_id) juftligi yangilanadi —
# boshqa videolar o'chirilmaydi.
# ============================================================

def add_movie(
    code,
    file_id,
    title="Nomsiz kino",
    genre=None,
    year=None,
    quality=None
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO movies
        (code, file_id, title, genre, year, quality, views, added_at)
        VALUES (?, ?, ?, ?, ?, ?, 0, datetime('now'))
        ON CONFLICT(code, file_id) DO UPDATE SET
            title = excluded.title,
            genre = COALESCE(excluded.genre, movies.genre),
            year = COALESCE(excluded.year, movies.year),
            quality = COALESCE(excluded.quality, movies.quality)
    """, (
        str(code).strip(),
        file_id,
        title,
        genre,
        year,
        quality
    ))

    connection.commit()
    connection.close()


# ============================================================
# 3. KOD BO'YICHA BITTA (birinchi) KINO — admin uchun
# ============================================================

def get_movie_by_code(code):

    movies = get_movies_by_code(code)

    if not movies:
        return None

    return movies[0]


# ============================================================
# 3b. KOD BO'YICHA BARCHA VIDEOLAR
# ============================================================

def get_movies_by_code(code):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            code,
            file_id,
            title,
            genre,
            year,
            quality,
            views,
            added_at
        FROM movies
        WHERE TRIM(code) = ?
        ORDER BY id ASC
    """, (str(code).strip(),))

    movies = cursor.fetchall()

    connection.close()

    return movies


# ============================================================
# 4. NOM BO'YICHA QIDIRISH (barcha mos videolar)
# ============================================================

def search_movies_by_title(query):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            code,
            file_id,
            title,
            genre,
            year,
            quality,
            views,
            added_at
        FROM movies
        WHERE title LIKE ?
        ORDER BY code ASC, id ASC
    """, (f"%{query}%",))

    movies = cursor.fetchall()

    connection.close()

    return movies


# ============================================================
# 4b. NOM BO'YICHA UNIKAL KODLAR (ro'yxat uchun)
# ============================================================

def search_movie_codes_by_title(query, limit=20):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            code,
            file_id,
            title,
            genre,
            year,
            quality,
            views,
            added_at
        FROM movies
        WHERE id IN (
            SELECT MIN(id)
            FROM movies
            WHERE title LIKE ?
            GROUP BY code
        )
        ORDER BY added_at DESC
        LIMIT ?
    """, (f"%{query}%", limit))

    movies = cursor.fetchall()

    connection.close()

    return movies


# ============================================================
# 5. KO'RISHNI OSHIRISH (kod bo'yicha barcha qatorlar)
# ============================================================

def increase_movie_views(code):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE movies
        SET views = COALESCE(views, 0) + 1
        WHERE code = ?
    """, (str(code).strip(),))

    connection.commit()
    connection.close()


# ============================================================
# 6. KINO O'CHIRISH (kod bo'yicha barcha videolar)
# ============================================================

def delete_movie(code):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM movies WHERE code = ?",
        (str(code).strip(),)
    )

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted


# ============================================================
# 7. KINO TAHRIRLASH (kod bo'yicha barcha videolar metadatasi)
# ============================================================

def update_movie(
    code,
    title,
    genre=None,
    year=None,
    quality=None
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE movies
        SET
            title = ?,
            genre = ?,
            year = ?,
            quality = ?
        WHERE code = ?
    """, (
        title,
        genre,
        year,
        quality,
        str(code).strip()
    ))

    updated = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return updated


# ============================================================
# 8. TOP KINOLAR (unikal kodlar)
# ============================================================

def get_top_movies(limit=10):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            code,
            file_id,
            title,
            genre,
            year,
            quality,
            views,
            added_at
        FROM movies
        WHERE id IN (
            SELECT MIN(id)
            FROM movies
            GROUP BY code
        )
        ORDER BY COALESCE(views, 0) DESC
        LIMIT ?
    """, (limit,))

    movies = cursor.fetchall()

    connection.close()

    return movies


# ============================================================
# 9. YANGI KINOLAR (unikal kodlar)
# ============================================================

def get_new_movies(limit=10):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            code,
            file_id,
            title,
            genre,
            year,
            quality,
            views,
            added_at
        FROM movies
        WHERE id IN (
            SELECT MAX(id)
            FROM movies
            GROUP BY code
        )
        ORDER BY added_at DESC
        LIMIT ?
    """, (limit,))

    movies = cursor.fetchall()

    connection.close()

    return movies


# ============================================================
# 10. RANDOM KINO (unikal kodning barcha videolari)
# ============================================================

def get_random_movie():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT code
        FROM movies
        GROUP BY code
        ORDER BY RANDOM()
        LIMIT 1
    """)

    row = cursor.fetchone()
    connection.close()

    if not row:
        return None

    movies = get_movies_by_code(row[0])
    return movies[0] if movies else None


def get_random_movies():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT code
        FROM movies
        GROUP BY code
        ORDER BY RANDOM()
        LIMIT 1
    """)

    row = cursor.fetchone()
    connection.close()

    if not row:
        return []

    return get_movies_by_code(row[0])


# ============================================================
# 11. KINOLAR SONI (unikal kodlar)
# ============================================================

def get_movies_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(DISTINCT code) FROM movies")

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# 12. KINOLAR SAHIFASI (unikal kodlar)
# ============================================================

def get_movies_page(page=1, per_page=10):

    connection = get_connection()
    cursor = connection.cursor()

    offset = (page - 1) * per_page

    cursor.execute("""
        SELECT
            code,
            file_id,
            title,
            genre,
            year,
            quality,
            views,
            added_at
        FROM movies
        WHERE id IN (
            SELECT MAX(id)
            FROM movies
            GROUP BY code
        )
        ORDER BY added_at DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))

    movies = cursor.fetchall()

    connection.close()

    return movies
