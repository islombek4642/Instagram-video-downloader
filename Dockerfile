# Python'ning rasmiy versiyasini asos qilib olamiz
FROM python:3.10-slim

# Ishchi direktoriyani o'rnatamiz
WORKDIR /app

# Tizim paketlarini yangilaymiz va ffmpeg o'rnatamiz
RUN apt-get update && apt-get install -y ffmpeg

# Kerakli kutubxonalar ro'yxatini nusxalaymiz
COPY requirements.txt .

# Kutubxonalarni o'rnatamiz
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini nusxalaymiz
COPY . .

# Botni ishga tushirish uchun buyruq
CMD ["python", "main.py"]
