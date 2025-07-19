import logging
import os
import re
import asyncio
from urllib.parse import urlparse

from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from moviepy.editor import VideoFileClip
from shazamio import Shazam
import instaloader

# .env faylidan muhit o'zgaruvchilarini yuklash
load_dotenv()

# Logger sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Instagram uchun Instaloader sozlamalari
L = instaloader.Instaloader(
    download_pictures=False,
    download_videos=True,
    download_video_thumbnails=False,
    download_geotags=False,
    download_comments=False,
    save_metadata=False,
    compress_json=False,
    # IP bloklanishini oldini olish uchun so'rovlar orasida tasodifiy pauza
    sleep=True,
    request_timeout=30,
)

# Proksi sozlamalari
PROXY = os.getenv("PROXY")
if PROXY:
    L.context.proxies = {
        'http': PROXY,
        'https': PROXY,
    }
    logger.info(f"Proksi-server ishlatilmoqda: {PROXY}")

# Instagram'ga kirish (ixtiyoriy, lekin tavsiya etiladi)
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

async def login_to_instagram():
    """Instagramga login qilish uchun asinxron funksiya."""
    if INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD:
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None, lambda: L.load_session_from_file(INSTAGRAM_USERNAME)
            )
            logger.info(f"{INSTAGRAM_USERNAME} uchun sessiya fayli topildi.")
        except FileNotFoundError:
            logger.info(f"{INSTAGRAM_USERNAME} uchun sessiya fayli topilmadi. Login qilinmoqda...")
            try:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    None, lambda: L.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
                )
                await loop.run_in_executor(
                    None, lambda: L.save_session_to_file()
                )
                logger.info(f"{INSTAGRAM_USERNAME} sifatida muvaffaqiyatli login qilindi.")
            except Exception as e:
                logger.error(f"Instagram'ga login qilishda xatolik: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start buyrug'i uchun javob qaytaradi."""
    await update.message.reply_html(
        'Assalomu alaykum! Instagram havolasini yuboring👇'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Foydalanuvchi xabarlarini (havolalarni) qayta ishlaydi."""
    message_text = update.message.text
    chat_id = update.message.chat_id

    # Instagram havolasini tekshirish
    url_match = re.search(r"(https?://www\.instagram\.com/([a-zA-Z0-9_\.]+)/([p,reel,tv]+)/([a-zA-Z0-9_\-]+))", message_text)
    if not url_match:
        await update.message.reply_text("Iltimos, to'g'ri Instagram havolasini yuboring.")
        return

    url = url_match.group(1)
    shortcode = url.split('/')[-2]
    
    processing_message = await update.message.reply_text("⏳ Havola tekshirilmoqda...")

    video_path = None
    audio_path = None

    try:
        # 1. Videoni yuklab olish
        await processing_message.edit_text("📥 Video yuklab olinmoqda...")
        loop = asyncio.get_event_loop()
        post = await loop.run_in_executor(
            None, lambda: instaloader.Post.from_shortcode(L.context, shortcode)
        )

        if not post.is_video:
            await processing_message.edit_text("Bu havola video emas. Iltimos, video havolasini yuboring.")
            return

        # Videoni yuklash
        target_dir = f"downloads/{chat_id}"
        os.makedirs(target_dir, exist_ok=True)
        await loop.run_in_executor(
            None, lambda: L.download_post(post, target=target_dir)
        )

        # Yuklangan fayl nomini topish
        for f in os.listdir(target_dir):
            if f.endswith('.mp4'):
                video_path = os.path.join(target_dir, f)
                break
        
        if not video_path:
            raise FileNotFoundError("Yuklangan video fayli topilmadi.")

        # 2. Audioni ajratib olish
        await processing_message.edit_text("🎵 Audio ajratib olinmoqda...")
        video_clip = VideoFileClip(video_path)
        if video_clip.audio is None:
            await processing_message.edit_text("Bu videoda ovoz mavjud emas.")
            # Ovoszsiz videoni yuborish
            await update.message.reply_video(video=open(video_path, 'rb'), caption="Bu videoda ovoz yo'q.")
            return

        audio_path = f"{video_path}.mp3"
        video_clip.audio.write_audiofile(audio_path, logger=None)
        video_clip.close()

        # 3. Musiqani aniqlash
        await processing_message.edit_text("🎶 Qo'shiq aniqlanmoqda...")
        shazam = Shazam()
        recognition_result = await shazam.recognize(audio_path)

        caption = "Qo'shiq aniqlanmadi"
        if recognition_result.get('track'):
            track_info = recognition_result['track']
            title = track_info.get('title', 'Noma\'lum')
            subtitle = track_info.get('subtitle', 'Noma\'lum')
            caption = f"🎵 Qo'shiq nomi: {title} - {subtitle}"

        # 4. Videoni foydalanuvchiga yuborish
        await processing_message.edit_text("✅ Tayyor! Video yuborilmoqda...")
        await update.message.reply_video(video=open(video_path, 'rb'), caption=caption)
        await processing_message.delete()

    except instaloader.exceptions.InstaloaderException as e:
        logger.error(f"Instaloader xatoligi: {e}")
        await processing_message.edit_text("Xatolik: Havola yaroqsiz yoki post maxfiy. Iltimos, qayta tekshiring.")
    except Exception as e:
        logger.error(f"Umumiy xatolik: {e}")
        await processing_message.edit_text("Noma'lum xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
    finally:
        # Vaqtinchalik fayllarni o'chirish
        if video_path and os.path.exists(video_path):
            os.remove(video_path)
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        # Papkani ham o'chirish
        target_dir = f"downloads/{chat_id}"
        if os.path.exists(target_dir) and not os.listdir(target_dir):
            os.rmdir(target_dir)

async def post_init(application: Application):
    """Bot ishga tushgandan so'ng bajariladigan amallar."""
    await login_to_instagram()
    await application.bot.set_my_commands([
        BotCommand("start", "Botni ishga tushirish")
    ])

def main() -> None:
    """Botni ishga tushiradi."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return

    # Ilovani yaratish
    application = Application.builder().token(token).post_init(post_init).build()

    # Handler'larni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Botni ishga tushirish
    logger.info("Bot ishga tushmoqda...")
    application.run_polling()

if __name__ == '__main__':
    main()
