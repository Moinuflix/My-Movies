import json
import urllib.request
import os

MAIN_DATA_PATH = "chunks/data_c01.json"
TRENDING_OUTPUT_PATH = "chunks/trending.json"
SIMKL_CLIENT_ID = "56fea6c62198dd45fa41015d7203fdf29978c5ff2b92f18ff86f0ce33d85f3a8"

# Strict Indian keywords & patterns
INDIAN_PATTERNS = [
    "tamil", "telugu", "hindi", "hin", "tam", "tel", "malayalam", "mal", "kannada", "kan",
    "bhooth", "karuppu", "dhurandhar", "behen", "udhayanidhi", "kollywood", "tollywood", "bollywood",
    "zee5", "sun nxt", "aha", "jiohs", "sonyliv", "hotstar"
]

def is_indian_movie(movie):
    name_str = str(movie.get("name", "")).lower()
    title_str = str(movie.get("title", "")).lower()
    orig_str = str(movie.get("original_title", "")).lower()
    plot_str = str(movie.get("plot", "")).lower()
    
    # Check Indian script characters (Devanagari, Tamil, Telugu, etc.)
    if any(ord(char) > 127 for char in orig_str):
        return True
        
    combined = f"{name_str} {title_str} {orig_str} {plot_str}"
    for kw in INDIAN_PATTERNS:
        if kw in combined:
            return True
    return False

def format_18_line(movies_list):
    entries = []
    for mv in movies_list:
        v_strs = []
        for ver in mv.get("versions", []):
            vs = (
                f'      {{\n'
                f'        "id": {json.dumps(ver.get("id",""))}, "name": {json.dumps(ver.get("name",""))}, "quality": {json.dumps(ver.get("quality",""))}, "source": {json.dumps(ver.get("source",""))}, "codec": {json.dumps(ver.get("codec",""))}, "resolution": {json.dumps(ver.get("resolution",""))}, "audio": {json.dumps(ver.get("audio",""))}, "channels": {json.dumps(ver.get("channels",""))},\n'
                f'        "stream_url": {json.dumps(ver.get("stream_url",""))},\n'
                f'        "specs": {json.dumps(ver.get("specs",{}))}\n'
                f'      }}'
            )
            v_strs.append(vs)
        all_vers = ",\n".join(v_strs)
        entry = (
            f'  {{\n'
            f'    "id": {json.dumps(mv.get("id",""))},\n'
            f'    "name": {json.dumps(mv.get("name",""))},\n'
            f'    "title": {json.dumps(mv.get("title",""))}, "original_title": {json.dumps(mv.get("original_title",""))}, "year": {mv.get("year", 0)},\n'
            f'    "tmdb_id": {mv.get("tmdb_id", 0)}, "imdb_id": {json.dumps(mv.get("imdb_id",""))}, "imdb_url": {json.dumps(mv.get("imdb_url",""))}, "rating": {mv.get("rating", 0)},\n'
            f'    "plot": {json.dumps(mv.get("plot",""))},\n'
            f'    "poster": {json.dumps(mv.get("poster",""))},\n'
            f'    "fanart": {json.dumps(mv.get("fanart",""))},\n'
            f'    "logo": {json.dumps(mv.get("logo",""))},\n'
            f'    "trailer": {json.dumps(mv.get("trailer",{}))},\n'
            f'    "stream_url": {json.dumps(mv.get("stream_url",""))},\n'
            f'    "badges": {json.dumps(mv.get("badges",{}))},\n'
            f'    "specs": {json.dumps(mv.get("specs",{}))},\n'
            f'    "versions": [\n{all_vers}\n    ]\n'
            f'  }}'
        )
        entries.append(entry)
    return "[\n" + ",\n".join(entries) + "\n]"

if not os.path.exists(MAIN_DATA_PATH):
    print(f"❌ Main data file not found at {MAIN_DATA_PATH}")
    exit(1)

with open(MAIN_DATA_PATH, "r", encoding="utf-8") as f:
    my_movies = json.load(f)

indian_pool = []
hollywood_pool = []

for m in my_movies:
    if is_indian_movie(m):
        indian_pool.append(m)
    else:
        hollywood_pool.append(m)

# Sort both: Latest Year First, then Best Rating
indian_sorted = sorted(indian_pool, key=lambda x: (int(x.get("year") or 0), float(x.get("rating") or 0)), reverse=True)
hollywood_sorted = sorted(hollywood_pool, key=lambda x: (int(x.get("year") or 0), float(x.get("rating") or 0)), reverse=True)

top_indian = indian_sorted[:6]
top_hollywood = hollywood_sorted[:4]

final_selection = top_indian + top_hollywood

os.makedirs(os.path.dirname(TRENDING_OUTPUT_PATH), exist_ok=True)
with open(TRENDING_OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(format_18_line(final_selection))

print(f"✅ Exact Top 10 Created: {len(top_indian)} Indian Movies + {len(top_hollywood)} Hollywood Movies!")
