# ============================================================
# UZ KINO BOT
# 7-FAYL: services/broadcast.py
# ============================================================
#
# Bu fayl ADMIN tomonidan yuboriladigan reklama va
# xabarlarni foydalanuvchilarga tarqatish uchun ishlaydi.
#
# Masalan admin:
#
# 📢 Yangi kino qo'shildi!
# 🎬 Avatar 2
#
# deb xabar yuborsa, bot bu xabarni foydalanuvchilarga
# tarqatadi.
#
# Bu yerda:
#
# 📢 Oddiy matn yuborish
# 🖼 Rasm yuborish
# 🎬 Video yuborish
# 📄 Hujjat yuborish
# 🔗 Tugmali xabarlarni nusxalash
#
# kabi imkoniyatlardan foydalanish mumkin.
# ============================================================

import asyncio

from aiogram import Bot

from bot.services.user_service import get_all_users


# ============================================================
# 1. XABARNI BARCHA FOYDALANUVCHILARGA YUBORISH
# ============================================================
#
# Bu funksiya admin yuborgan xabarni olib,
# barcha foydalanuvchilarga nusxalab yuboradi.
#
# copy_message() ishlatilgani uchun:
#
# - matn
# - rasm
# - video
# - audio
# - hujjat
# - sticker
# - tugmalar
#
# kabi Telegram xabarlarining ko'p turlarini yuborish mumkin.
# ============================================================

async def broadcast_message(
    bot: Bot,
    from_chat_id: int,
    message_id: int
):

    # Bazadan barcha foydalanuvchilarni olamiz
    users = get_all_users()

    # Muvaffaqiyatli yuborilgan xabarlar soni
    success = 0

    # Yuborilmagan xabarlar soni
    failed = 0

    # Har bir foydalanuvchiga xabar yuboramiz
    for user in users:

        user_id = user[0]

        try:

            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=from_chat_id,
                message_id=message_id
            )

            success += 1

        except Exception:

            # Masalan:
            # foydalanuvchi botni bloklagan bo'lishi mumkin.
            failed += 1

        # Telegram serveriga juda ko'p so'rov yubormaslik
        # uchun ozgina kutamiz.
        await asyncio.sleep(0.05)

    # Natijani qaytaramiz
    return {
        "success": success,
        "failed": failed,
        "total": len(users)
    }


# ============================================================
# 2. FAQAT BIR FOYDALANUVCHIGA XABAR YUBORISH
# ============================================================
#
# Keyinchalik admin ma'lum bir foydalanuvchiga xabar
# yuborishi kerak bo'lsa, shu funksiyadan foydalanamiz.
# ============================================================

async def send_to_user(
    bot: Bot,
    user_id: int,
    from_chat_id: int,
    message_id: int
):

    try:

        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=from_chat_id,
            message_id=message_id
        )

        return True

    except Exception:

        return False


# ============================================================
# 3. REKLAMA NATIJASINI CHIROYLI KO'RINISHDA TAYYORLASH
# ============================================================
#
# Admin reklama yuborgandan keyin quyidagiga o'xshash
# ma'lumot oladi:
#
# 📢 REKLAMA YAKUNLANDI
#
# 👥 Jami: 1000
# ✅ Yetkazildi: 950
# ❌ Yetkazilmadi: 50
# ============================================================

def format_broadcast_result(result):

    return (
        "📢 <b>REKLAMA YAKUNLANDI</b>\n\n"
        f"👥 Jami foydalanuvchilar: "
        f"{result['total']}\n"
        f"✅ Yetkazildi: "
        f"{result['success']}\n"
        f"❌ Yetkazilmadi: "
        f"{result['failed']}"
    )
