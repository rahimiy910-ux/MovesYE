#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎬 ارسال پست حرفه‌ای فیلم به کانال
با قالب اختصاصی ویو فیلم
"""

import os
import asyncio
import random
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import pytz

# ==================== ایموجی‌ها ====================

GENRE_EMOJI = {
    'اکشن': '💥', 'کمدی': '😂', 'درام': '🎭',
    'ترسناک': '👻', 'علمی تخیلی': '🚀', 'عاشقانه': '💕',
    'هیجانی': '⚡', 'معمایی': '🔍', 'انیمیشن': '🎨',
    'جنایی': '🕵️', 'ماجراجویی': '🗺️', 'فانتزی': '🧙',
    'جنگی': '⚔️', 'تاریخی': '📜', 'زندگی‌نامه': '📖'
}

RATING_STARS = {
    (9.0, 10.0): "🏆🏆🏆🏆🏆",
    (8.0, 8.9): "⭐️⭐️⭐️⭐️",
    (7.0, 7.9): "⭐️⭐️⭐️",
    (6.0, 6.9): "⭐️⭐️",
    (0, 5.9): "⭐️"
}

def get_stars(rating):
    try:
        r = float(rating)
        for (low, high), stars in RATING_STARS.items():
            if low <= r <= high:
                return stars
    except:
        pass
    return "⭐️⭐️⭐️"

def get_time_emoji():
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "☀️"
    elif 12 <= hour < 17:
        return "🌤"
    elif 17 <= hour < 20:
        return "🌅"
    else:
        return "🌙"

def get_greeting(time_name):
    greetings = {
        "ظهر": [
            "🎬 فیلم ظهرت رو انتخاب کن...",
            "🍿 یه فیلم برای عصر...",
            "🎥 امروز اینو ببین..."
        ],
        "شب": [
            "🌙 امشب چی ببینیم؟",
            "🍿 فیلم امشب...",
            "🎬 امشب این فیلم رو از دست نده...",
            "🌃 بهترین انتخاب برای امشب..."
        ]
    }
    return random.choice(greetings.get(time_name, ["🎬 پیشنهاد امروز..."]))

def format_movie_post(movie, time_name):
    """قالب حرفه‌ای پست فیلم"""
    
    # اطلاعات اصلی
    title = movie.get('title', 'عنوان نامشخص')
    year = movie.get('year', '')
    rating = movie.get('rating', 'N/A')
    source = movie.get('source', 'TMDB')
    summary = movie.get('summary_fa', '')
    director = movie.get('director', 'نامشخص')
    cast = movie.get('cast', [])
    genres = movie.get('genres_fa', [])
    duration = movie.get('duration', 'نامشخص')
    imdb_link = movie.get('imdb_link', 'https://www.imdb.com')
    
    # پردازش
    stars = get_stars(rating)
    
    # ژانر با ایموجی
    genre_parts = []
    for g in genres[:3]:
        emoji = GENRE_EMOJI.get(g, '🎬')
        genre_parts.append(f"{emoji} {g}")
    genre_text = "  |  ".join(genre_parts) if genre_parts else "🎬 فیلم"
    
    # بازیگران
    cast_text = "، ".join(cast[:5]) if cast else "بازیگران برجسته"
    
    # خلاصه (محدود)
    if len(summary) > 400:
        summary = summary[:400] + "..."
    if not summary:
        summary = "برای مشاهده خلاصه داستان به لینک IMDB مراجعه کنید"
    
    # ایموجی پست
    time_emoji = get_time_emoji()
    greeting = get_greeting(time_name)
    
    # شماره تصادفی برای تنوع
    post_number = random.randint(100, 999)
    
    # ساخت کپشن
    caption = f"""{time_emoji} {greeting}

🎬 **{title}** ({year})

{stars}  **{rating}**/10

🎭 {genre_text}

━━━━━━━━━━━━━━━━━━━

🎬 **کارگردان:**
{director}

👥 **بازیگران:**
{cast_text}

⏱️ **مدت زمان:**
{duration}

━━━━━━━━━━━━━━━━━━━

📝 **داستان فیلم:**

{summary}

━━━━━━━━━━━━━━━━━━━

🔗 [مشاهده در IMDB]({imdb_link})

📡 {source}

🎬 **#VioFilm | #ویو_فیلم**
#معرفی_فیلم #پیشنهاد_فیلم
{genre_parts[0].split()[1] if genre_parts else '#سینما'}

🆔 @VioFilm"""
    
    return caption

async def send_movie_post(movie, time_name="شب"):
    """ارسال پست به کانال"""
    
    token = os.environ.get("VIOFILM_BOT_TOKEN")
    chat_id = os.environ.get("VIOFILM_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ تنظیمات ناقص")
        return False
    
    bot = Bot(token=token)
    
    try:
        caption = format_movie_post(movie, time_name)
        poster = movie.get('poster', '')
        
        if poster and poster.startswith('http') and len(poster) > 20:
            # ارسال با پوستر
            await bot.send_photo(
                chat_id=chat_id,
                photo=poster,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN
            )
            print(f"   🖼️ ارسال با پوستر")
        else:
            # ارسال متنی
            await bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=False
            )
            print(f"   📝 ارسال متنی (بدون پوستر)")
        
        return True
        
    except TelegramError as e:
        error_msg = str(e)
        if "chat not found" in error_msg.lower():
            print("   ❌ کانال پیدا نشد")
        elif "not enough rights" in error_msg.lower():
            print("   ❌ ربات ادمین نیست")
        else:
            print(f"   ❌ خطا: {error_msg[:80]}")
        return False
        
    except Exception as e:
        print(f"   ❌ خطا: {e}")
        return False
