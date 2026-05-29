#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎬 جوینده هوشمند فیلم با TMDB API
هر روز ۲ فیلم متفاوت و غیرتکراری
"""

import requests
import random
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from deep_translator import GoogleTranslator

# ==================================================
# 📁 تنظیمات اولیه
# ==================================================

DATA_DIR = Path('data')
HISTORY_FILE = DATA_DIR / 'movie_history.json'
COOLDOWN_DAYS = 45

# 🔑 API Key تو (همون دومی که گرفتی)
TMDB_API_KEY = "b720e1c8103f7eb7da831c5268ea5cb0"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    'Accept': 'application/json',
}

# ==================================================
# 🌐 ترجمه به فارسی
# ==================================================

def translate_to_fa(text, max_length=400):
    """ترجمه به فارسی"""
    if not text or len(text.strip()) < 3:
        return text
    
    # اگه already فارسی بود
    persian_chars = len([c for c in text if '\u0600' <= c <= '\u06FF'])
    if persian_chars > len(text) * 0.3:
        return text
    
    try:
        translator = GoogleTranslator(source='en', target='fa')
        return translator.translate(text[:max_length])
    except:
        return text

# ==================================================
# 🎬 دریافت فیلم‌ها از TMDB
# ==================================================

def fetch_tmdb(endpoint, params=None):
    """درخواست به TMDB API"""
    url = f"{TMDB_BASE_URL}/{endpoint}"
    default_params = {'api_key': TMDB_API_KEY}
    if params:
        default_params.update(params)
    
    try:
        response = requests.get(url, params=default_params, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"   ❌ خطا در TMDB: {e}")
        return None

def get_popular_movies(limit=20):
    """فیلم‌های محبوب روز"""
    print("   📡 فیلم‌های محبوب TMDB...")
    data = fetch_tmdb('movie/popular', {'language': 'en-US'})
    
    movies = []
    if data and 'results' in data:
        for item in data['results'][:limit]:
            movies.append({
                'id': item['id'],
                'title': item['title'],
                'rating': round(item['vote_average'], 1),
                'year': item['release_date'][:4] if item['release_date'] else 'نامشخص',
                'source': 'TMDB محبوب'
            })
    print(f"   ✅ {len(movies)} فیلم")
    return movies

def get_top_rated_movies(limit=20):
    """فیلم‌های برتر تاریخ"""
    print("   📡 فیلم‌های برتر TMDB...")
    data = fetch_tmdb('movie/top_rated', {'language': 'en-US'})
    
    movies = []
    if data and 'results' in data:
        for item in data['results'][:limit]:
            movies.append({
                'id': item['id'],
                'title': item['title'],
                'rating': round(item['vote_average'], 1),
                'year': item['release_date'][:4] if item['release_date'] else 'نامشخص',
                'source': 'TMDB برتر'
            })
    print(f"   ✅ {len(movies)} فیلم")
    return movies

def get_upcoming_movies(limit=20):
    """فیلم‌های در حال اکران یا به‌زودی"""
    print("   📡 فیلم‌های جدید TMDB...")
    data = fetch_tmdb('movie/upcoming', {'language': 'en-US'})
    
    movies = []
    if data and 'results' in data:
        for item in data['results'][:limit]:
            movies.append({
                'id': item['id'],
                'title': item['title'],
                'rating': round(item['vote_average'], 1) if item['vote_average'] else 'جدید',
                'year': item['release_date'][:4] if item['release_date'] else 'به‌زودی',
                'source': 'TMDB جدید'
            })
    print(f"   ✅ {len(movies)} فیلم")
    return movies

def get_movie_details(movie_id):
    """دریافت اطلاعات کامل یک فیلم با ID"""
    print("   🔍 جزئیات فیلم...")
    
    # اطلاعات اصلی
    data = fetch_tmdb(f'movie/{movie_id}', {'language': 'en-US', 'append_to_response': 'credits'})
    
    if not data:
        return {}
    
    details = {}
    
    # خلاصه داستان (انگلیسی برای ترجمه بهتر)
    if data.get('overview'):
        details['summary_en'] = data['overview']
        details['summary_fa'] = translate_to_fa(data['overview'], 400)
    else:
        details['summary_fa'] = "خلاصه داستان موجود نیست"
    
    # کارگردان (از credits)
    directors = []
    if 'credits' in data and 'crew' in data['credits']:
        for crew in data['credits']['crew']:
            if crew.get('job') == 'Director':
                directors.append(crew['name'])
    details['director'] = ', '.join(directors) if directors else "نامشخص"
    
    # بازیگران (۵ نفر اول)
    cast = []
    if 'credits' in data and 'cast' in data['credits']:
        for actor in data['credits']['cast'][:5]:
            cast.append(actor['name'])
    details['cast'] = cast if cast else ["نامشخص"]
    
    # ژانرها به فارسی
    genre_fa_map = {
        'Action': 'اکشن', 'Comedy': 'کمدی', 'Drama': 'درام',
        'Horror': 'ترسناک', 'Science Fiction': 'علمی تخیلی', 'Romance': 'عاشقانه',
        'Thriller': 'هیجانی', 'Mystery': 'معمایی', 'Animation': 'انیمیشن',
        'Crime': 'جنایی', 'Adventure': 'ماجراجویی', 'Fantasy': 'فانتزی',
        'War': 'جنگی', 'History': 'تاریخی', 'Documentary': 'مستند',
        'Family': 'خانوادگی', 'Music': 'موسیقی', 'Western': 'وسترن'
    }
    genres = []
    for genre in data.get('genres', []):
        genre_en = genre['name']
        genres.append(genre_fa_map.get(genre_en, genre_en))
    details['genres_fa'] = genres if genres else ["متفرقه"]
    
    # مدت زمان
    runtime = data.get('runtime')
    details['duration'] = f"{runtime} دقیقه" if runtime else "نامشخص"
    
    # پوستر
    poster_path = data.get('poster_path')
    if poster_path:
        details['poster'] = f"https://image.tmdb.org/t/p/w500{poster_path}"
    else:
        details['poster'] = ""
    
    # لینک IMDB (اگه داشته باشه)
    imdb_id = data.get('imdb_id')
    if imdb_id:
        details['imdb_link'] = f"https://www.imdb.com/title/{imdb_id}/"
    else:
        details['imdb_link'] = f"https://www.themoviedb.org/movie/{movie_id}"
    
    return details

# ==================================================
# 📜 مدیریت تاریخچه (جلوگیری از تکرار)
# ==================================================

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return []

def save_history(history):
    os.makedirs(DATA_DIR, exist_ok=True)
    cutoff = (datetime.now() - timedelta(days=COOLDOWN_DAYS)).isoformat()
    history = [h for h in history if h.get('date', '') > cutoff]
    history = history[-300:]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def is_duplicate(title, history):
    title_clean = title.lower().strip()
    for h in history:
        if h['title'].lower().strip() == title_clean:
            return True
    return False

# ==================================================
# 🎯 دریافت فیلم‌های امروز
# ==================================================

def get_todays_movies(count=2):
    """دریافت فیلم‌های امروز (بدون تکرار)"""
    
    history = load_history()
    
    # جمع‌آوری از منابع مختلف
    all_movies = []
    all_movies.extend(get_popular_movies(25))
    all_movies.extend(get_top_rated_movies(20))
    all_movies.extend(get_upcoming_movies(15))
    
    # حذف تکراری‌ها (بر اساس عنوان)
    unique_movies = {}
    for movie in all_movies:
        if movie['title'] not in unique_movies:
            unique_movies[movie['title']] = movie
    all_movies = list(unique_movies.values())
    
    # حذف فیلم‌های دیده شده از تاریخچه
    new_movies = []
    for movie in all_movies:
        if not is_duplicate(movie['title'], history):
            new_movies.append(movie)
    
    # اگه فیلم جدید کافی نبود
    if len(new_movies) < count:
        print(f"   ⚠️ فقط {len(new_movies)} فیلم جدید! آزادسازی تاریخچه...")
        if len(history) > 50:
            history = history[20:]
            save_history(history)
            return get_todays_movies(count)
    
    # انتخاب تصادفی
    selected = random.sample(new_movies, min(count, len(new_movies)))
    
    # دریافت جزئیات کامل برای هر فیلم
    full_movies = []
    for movie in selected:
        print(f"\n   🎬 {movie['title']} ({movie['year']})")
        
        details = get_movie_details(movie['id'])
        
        full_movie = {**movie, **details}
        full_movies.append(full_movie)
        
        # ذخیره در تاریخچه
        history.append({
            'title': full_movie['title'],
            'date': datetime.now().isoformat()
        })
    
    save_history(history)
    
    print(f"\n   ✅ {len(full_movies)} فیلم نهایی")
    return full_movies

# ==================================================
# 🚀 اجرای تست
# ==================================================

if __name__ == "__main__":
    print("🎬 شروع جستجوی فیلم‌های امروز...\n")
    movies = get_todays_movies(2)
    
    print("\n" + "="*50)
    for i, movie in enumerate(movies, 1):
        print(f"\n{i}. 🎬 {movie['title']} ({movie['year']})")
        print(f"   ⭐ امتیاز: {movie['rating']}")
        print(f"   🎭 ژانر: {', '.join(movie.get('genres_fa', []))}")
        print(f"   🎬 کارگردان: {movie.get('director', 'نامشخص')}")
        print(f"   👥 بازیگران: {', '.join(movie.get('cast', [])[:3])}")
        print(f"   📝 خلاصه: {movie.get('summary_fa', 'ندارد')[:150]}...")
    print("\n" + "="*50)
