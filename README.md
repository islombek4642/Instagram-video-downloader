# Instagram Video Downloader Telegram Bot

Bu Telegram bot Instagram'dan video, post yoki reel yuklab oladi, undagi musiqani aniqlaydi va natijani foydalanuvchiga yuboradi.

## Funksiyalar

- Instagram havolalarini qabul qiladi.
- Videoni yuklab oladi.
- Videodan audioni ajratib oladi.
- Shazamio yordamida musiqa nomini aniqlaydi.
- Videoga musiqa nomini izoh sifatida qo'shib, foydalanuvchiga yuboradi.
- Musiqa topilmasa yoki video ovozsiz bo'lsa, xabar beradi.
- Noto'g'ri havolalar uchun xatolik xabarini chiqaradi.

## O'rnatish va ishga tushirish

### 1. Loyihani yuklab oling:
```bash
git clone https://github.com/your-username/instagram-downloader-bot.git
cd instagram-downloader-bot
```

### 2. `.env` faylini sozlang:

`.env` faylini yarating va kerakli ma'lumotlarni kiriting:

```
TELEGRAM_BOT_TOKEN="SIZNING_TELEGRAM_BOT_TOKENINGIZ"
INSTAGRAM_USERNAME="SIZNING_INSTAGRAM_PROFILINGIZ_NOMI" # Ixtiyoriy, lekin tavsiya etiladi
INSTAGRAM_PASSWORD="SIZNING_INSTAGRAM_PROFILINGIZ_PAROLI" # Ixtiyoriy, lekin tavsiya etiladi

# Proksi-server (ixtiyoriy, IP bloklanishini oldini olish uchun)
# Format: http://user:pass@host:port yoki socks5://user:pass@host:port
PROXY=""
```

### 3. Docker orqali ishga tushirish:

Docker kompyuteringizda o'rnatilgan bo'lishi kerak.

```bash
docker build -t instagram-bot .
docker run -d --env-file .env --name instagram-bot-container instagram-bot
```

### 4. Mahalliy (Docker'siz) ishga tushirish:

Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

Botni ishga tushiring:
```bash
python main.py
```

## Railway'ga joylashtirish

1. Loyihangizni GitHub'ga yuklang.
2. Railway.app saytida yangi loyiha yarating va GitHub repozitoriyni ulang.
3. `Dockerfile` avtomatik tarzda aniqlanadi.
4. `Variables` bo'limiga o'ting va `.env` faylidagi o'zgaruvchilarni (TELEGRAM_BOT_TOKEN, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD) qo'shing.
5. Deploy tugmasini bosing.
