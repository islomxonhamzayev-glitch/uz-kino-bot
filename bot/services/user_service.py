# ============================================================
# UZ KINO BOT
# 6-FAYL: services/user_service.py
# ============================================================
#
# Bu fayl FOYDALANUVCHILAR bilan bog'liq barcha ishlarni
# boshqaradi.
#
# Masalan:
#
# 👤 Foydalanuvchini saqlash
# 🔎 Foydalanuvchini topish
# 📊 Foydalanuvchilar sonini olish
# ❤️ Sevimli kinolarni boshqarish
# 🔗 Referral tizimi
#
# Admin panel foydalanuvchilar haqida ma'lumot kerak bo'lsa,
# shu fayldagi funksiyalardan foydalanadi.
# ============================================================

from bot.database import get_connection


# ============================================================
# 1. FOYDALANUVCHINI SAQLASH
# ============================================================
#
# Foydalanuvchi /start bosganda yoki botdan foydalanganda
# uning ma'lumotlarini bazaga saqlaymiz.
#
# Agar foydalanuvchi oldin bazada bo'lsa,
# ma'lumotlari yangilanadi.
# ============================================================

def save_user(
    user_id,
    username,
    first_name
):

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
# 2. FOYDALANUVCHINI ID ORQALI TOPISH
# ============================================================
#
# Telegram ID orqali foydalanuvchi haqida ma'lumot olamiz.
# ============================================================

def get_user(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            user_id,
            username,
            first_name,
            joined_at,
            referrals
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    return user


# ============================================================
# 3. BARCHA FOYDALANUVCHILAR
# ============================================================
#
# Reklama yuborishda barcha user_id lar kerak bo'ladi.
# ============================================================

def get_all_users():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT user_id
        FROM users
    """)

    users = cursor.fetchall()

    connection.close()

    return users


# ============================================================
# 4. FOYDALANUVCHILAR SONI
# ============================================================

def get_users_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# 5. BUGUN QO'SHILGAN FOYDALANUVCHILAR
# ============================================================
#
# Admin statistikada:
#
# 👥 Bugun: 25
#
# kabi ma'lumotni ko'rsatishimiz mumkin.
# ============================================================

def get_today_users_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM users
        WHERE DATE(joined_at) = DATE('now')
    """)

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# 6. REFERRALNI HISOBLASH
# ============================================================
#
# Bir foydalanuvchi boshqa odamni botga olib kelsa,
# uning referrals sonini 1 taga oshiramiz.
# ============================================================

def increase_referrals(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE users
        SET referrals = referrals + 1
        WHERE user_id = ?
    """, (user_id,))

    connection.commit()
    connection.close()


# ============================================================
# 7. REFERRAL SONINI OLISH
# ============================================================

def get_referral_count(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT referrals
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    result = cursor.fetchone()

    connection.close()

    if result:
        return result[0]

    return 0


# ============================================================
# 8. KINO SEVIMLILARGA QO'SHISH
# ============================================================
#
# Foydalanuvchi:
#
# ❤️ Sevimlilarga
#
# tugmasini bosganda kino shu jadvalga yoziladi.
# ============================================================

def add_favorite(
    user_id,
    movie_code
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO favorites (
            user_id,
            movie_code
        )
        VALUES (?, ?)
    """, (
        user_id,
        movie_code
    ))

    connection.commit()
    connection.close()


# ============================================================
# 9. SEVIMLILARDAN O'CHIRISH
# ============================================================

def remove_favorite(
    user_id,
    movie_code
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM favorites
        WHERE user_id = ?
        AND movie_code = ?
    """, (
        user_id,
        movie_code
    ))

    connection.commit()
    connection.close()


# ============================================================
# 10. KINO SEVIMLILARDA BOR-YO'QLIGINI TEKSHIRISH
# ============================================================

def is_favorite(
    user_id,
    movie_code
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM favorites
        WHERE user_id = ?
        AND movie_code = ?
    """, (
        user_id,
        movie_code
    ))

    result = cursor.fetchone()

    connection.close()

    return result is not None


# ============================================================
# 11. FOYDALANUVCHINING SEVIMLI KINOLARI
# ============================================================
#
# Foydalanuvchi "❤️ Sevimlilar" tugmasini bosganda
# shu funksiyadan foydalanamiz.
# ============================================================

def get_favorite_movies(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            movies.code,
            movies.title,
            movies.genre,
            movies.year,
            movies.quality
        FROM favorites

        INNER JOIN movies
        ON favorites.movie_code = movies.code

        WHERE favorites.user_id = ?
          AND movies.id IN (
              SELECT MIN(id)
              FROM movies
              GROUP BY code
          )

        ORDER BY favorites.id DESC
    """, (user_id,))

    movies = cursor.fetchall()

    connection.close()

    return movies


# ============================================================
# 12. FOYDALANUVCHINING SEVIMLI KINOLARI SONI
# ============================================================

def get_favorites_count(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM favorites
        WHERE user_id = ?
    """, (user_id,))

    count = cursor.fetchone()[0]

    connection.close()

    return count
