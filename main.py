#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎵 VIBE MUSIC | وایب موزیک
یه موزیک... یه حس... یه وایب...
نسخه نهایی - روزی ۲ پست
"""

import asyncio
import sys
import os
from datetime import datetime
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from music_finder import get_fresh_music
from caption_engine import get_unique_caption
from vibe_sender import send_vibe_post

async def main():
    print("\n" + "=" * 60)
    print("🎵  VIBE MUSIC | وایب موزیک")
    print("     یه موزیک... یه حس... یه وایب...")
    print("=" * 60)
    
    now = datetime.now()
    hour = now.hour
    
    # تشخیص صبح یا شب
    if 5 <= hour < 12:
        time_name = "صبح"
        mood_preference = ["غمگین", "عاشقانه"]
    else:
        time_name = "شب"
        mood_preference = ["گنگ", "خودستایانه", "غمگین"]
    
    print(f"🌅 {time_name} بخیر | {now.strftime('%H:%M')}")
    print(f"🎭 انتخاب از بین: {', '.join(mood_preference)}")
    print("-" * 60)
    
    try:
        # 1. پیدا کردن موزیک جدید
        print("\n🎧 [1/3] جستجوی موزیک...")
        music = get_fresh_music(mood_preference)
        
        if not music:
            print("❌ موزیک جدید پیدا نشد")
            return
        
        print(f"   🎵 {music['title']}")
        print(f"   👤 {music['artist']}")
        print(f"   🏷️ {music['mood']} | {music.get('year','')}")
        
        # 2. انتخاب کپشن یکتا
        print("\n✍️ [2/3] انتخاب کپشن...")
        caption = get_unique_caption(music['mood'])
        print(f"   💬 {caption[:70]}...")
        
        # 3. ارسال به کانال
        print("\n🚀 [3/3] ارسال به کانال @VibeMusic...")
        result = await send_vibe_post(music, caption)
        
        if result:
            print("\n✨ پست ارسال شد!")
            print(f"   🎵 {music['title']} - {music['artist']}")
            print(f"   💬 {caption[:50]}...")
        else:
            print("\n❌ ارسال ناموفق")
        
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())