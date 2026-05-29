#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎬 ارسال پست حرفه‌ای فیلم به کانال
با قالب اختصاصی ویو فیلم
"""

import os
import asyncio
import random
import re
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

# ==================== ایموجی‌ها ====================

GENRE_EMOJI = {
    'اکشن': '💥', 'کمدی': '😂', 'درام': '🎭', 'ترسناک': '😱',
    'علمی تخیلی': '🚀', 'عاشقانه': '💕', 'هیجانی': '⚡', 'معمایی': '🔍',
    'انیمیشن': '🎨', 'جنایی': '🕵️', 'ماجراجویی': '🗺️', 'فانتزی': '✨',
    'جنگی': '⚔️', 'تاریخی': '🏛️', 'خانوادگی': '👨‍👩‍👧', 'مستند': '📹'
}

RATING_STARS = {
    (9.0, 10.0): "🏆🏆🏆🏆🏆",
    (8.0, 8.9): "⭐️⭐️⭐️⭐️",
    (7.0, 7.9): "⭐️⭐️⭐️",
    (6.0, 6.9): "⭐️⭐️",
    (0, 5.9): "⭐️"
}

def escape_markdown_v2(text):
    """ایسکیپ کاراکترهای خاص مارکداون V2 تلگرام (بجز > که برای نقل قول است)"""
    if not text:
        return text
    # کاراکترهایی که باید ایسکیپ شوند (بجز >)
    special_chars = r'([_*\[\]()~`#+\-=|{}.!\\])'
    return re.sub(special_chars, r'\\\1', str(text))

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
    if time_name == "ظهر":
        return "✨ *پیشنهاد ویژه ظهر* ✨"
    else:
        return "🌟 *پیشنهاد ویژه شب* 🌟"

def format_movie_post(movie, time_name):
    """قالب حرفه‌ای با فرمت‌بندی کامل مارکداون V2 و بلاک‌کوت"""
    
    # اطلاعات اصلی
    title = movie.get('title', 'عنوان نامشخص')
    year = movie.get('year', '')
    rating = movie.get('rating', 'N/A')
    summary = movie.get('summary_fa', '')
    director = movie.get('director', 'نامشخص')
    cast = movie.get('cast', [])
    genres = movie.get('genres_fa', [])
    duration = movie.get('duration', 'نامشخص')
    imdb_link = movie.get('imdb_link', '')
    
    # ایمنی برای مارکداون V2
    title = escape_markdown_v2(title)
    summary = escape_markdown_v2(summary[:250]) if len(summary) > 250 else escape_markdown_v2(summary)
    director = escape_markdown_v2(director)
    
    # امتیاز با ستاره
    stars = get_stars(rating)
    
    # ژانرها با فرمت بولت
    genre_list = []
    for g in genres[:3]:
        emoji = GENRE_EMOJI.get(g, '🎬')
        genre_list.append(f"*{emoji} {g}*")
    genre_text = "  •  ".join(genre_list) if genre_list else "*🎬 فیلم*"
    
    # بازیگران (حداکثر ۳ نفر)
    if cast:
        cast_list = [f"*{escape_markdown_v2(a)}*" for a in cast[:3]]
        cast_text = "  •  ".join(cast_list)
    else:
        cast_text = "*—*"
    
    # ایموجی و متن خوش‌آمدگویی
    time_emoji = get_time_emoji()
    greeting = get_greeting(time_name)
    
    # ساخت کپشن نهایی
    caption = f"""{time_emoji} {greeting} {time_emoji}

╭━━━━━━━━━━━━━━━━━━━━╮
┃ 🎬 *{title}* `({year})`
╰━━━━━━━━━━━━━━━━━━━━╯

{stars}  `⭐ {rating}/10`

{genre_text}

┌─────────────────────
│ 🎭 *کارگردان* → `{director}`
│ 👥 *بازیگران* → {cast_text}
│ ⏱️ *مدت زمان* → `{duration}`
└─────────────────────

📖 *خلاصه داستان*

> {summary}

━━━━━━━━━━━━━━━━━━━━
🔗 [🎬 *مشاهده در IMDB*]({imdb_link})
━━━━━━━━━━━━━━━━━━━━

{time_emoji} `#VioFilm`  `#{title.replace(' ', '_')}`  `#پیشنهاد_فیلم`
"""
    
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
            await bot.send_photo(
                chat_id=chat_id,
                photo=poster,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            print(f"   🖼️ ارسال با پوستر")
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode=ParseMode.MARKDOWN_V2,
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
        elif "can't parse entities" in error_msg.lower():
            print("   ❌ مشکل در قالب متن - ارسال بدون مارکداون")
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode=None,
                    disable_web_page_preview=False
                )
                print("   ✅ ارسال شد (بدون فرمت)")
                return True
            except:
                pass
        else:
            print(f"   ❌ خطا: {error_msg[:80]}")
        return False
        
    except Exception as e:
        print(f"   ❌ خطا: {e}")
        return False
