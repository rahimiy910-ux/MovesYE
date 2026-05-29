#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎬 VIO FILM | ویو فیلم
امشب چی ببینیم؟
نسخه 1.0 - روزی ۲ فیلم
"""

import asyncio
import sys
import os
from datetime import datetime
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from movie_finder import get_todays_movies
from movie_sender import send_movie_post

async def main():
    print("\n" + "=" * 65)
    print("🎬  VIO FILM | ویو فیلم")
    print("     امشب چی ببینیم؟")
    print("=" * 65)
    
    now = datetime.now()
    hour = now.hour
    
    if 8 <= hour < 16:
        time_name = "ظهر"
        count = 2
    else:
        time_name = "شب"
        count = 2
    
    print(f"⏰ {time_name} بخیر | {now.strftime('%H:%M')}")
    print(f"🎬 دریافت {count} فیلم برای امروز")
    print("-" * 65)
    
    try:
        # 1. جستجوی فیلم‌ها
        print("\n🎬 [1/3] جستجوی فیلم‌های امروز...")
        movies = get_todays_movies(count=count)
        
        if not movies:
            print("❌ فیلمی پیدا نشد")
            return
        
        print(f"   📊 {len(movies)} فیلم آماده شد:")
        for i, m in enumerate(movies, 1):
            rating = m.get('rating', 'N/A')
            print(f"   {i}. {m['title']} ⭐{rating}")
        
        # 2. ارسال
        print(f"\n🚀 [2/3] ارسال به @VioFilm...")
        
        sent = 0
        for i, movie in enumerate(movies, 1):
            print(f"\n   📤 فیلم {i}/{len(movies)}")
            result = await send_movie_post(movie, time_name)
            if result:
                sent += 1
                print(f"   ✅ ارسال شد")
            else:
                print(f"   ❌ خطا در ارسال")
            
            if i < len(movies):
                await asyncio.sleep(2)
        
        # 3. گزارش
        print(f"\n📊 [3/3] گزارش نهایی:")
        print(f"   ✅ {sent} فیلم ارسال شد")
        print(f"   📅 {now.strftime('%Y/%m/%d')}")
        
        print("\n✨ پایان موفق!")
        print("=" * 65 + "\n")
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())