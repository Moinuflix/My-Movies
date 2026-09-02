import json
import os
import urllib.request

MAIN_DATA_PATH = "chunks/data_c01.json"
TRENDING_OUTPUT_PATH = "chunks/trending.json"
ADMIN_PASS = "moinu_secret_2026"
ALLOWED_AGENT = "Kodi-MoinuTV-PrivatePlayer/1.0"

# Strict Indian keywords & patterns
INDIAN_PATTERNS = [
    "tamil",
    "telugu",
    "hindi",
    "hin",
    "tam",
    "tel",
    "malayalam",
    "mal",
    "kannada",
    "kan",
    "bhooth",
    "karuppu",
    "dhurandhar",
    "behen",
    "udhayanidhi",
    "kollywood",
    "tollywood",
    "bollywood",
    "zee5",
    "sun nxt",
    "aha",
    "jiohs",
    "sonyliv",
    "hotstar",
]


def fix_stream_url(url):
  if not url:
    return ""
  # Agar Cloudflare Worker link hai aur pass missing hai toh inject karein
  if "workers.dev" in url:
    clean_url = url.split("|")[0]
    if "pass=" not in clean_url:
      sep = "&" if "?" in clean_url else "?"
      clean_url = f"{clean_url}{sep}pass={ADMIN_PASS}"
    return f"{clean_url}|User-Agent={ALLOWED_AGENT}"
  return url


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
      v_stream = fix_stream_url(ver.get("stream_url", ""))
      vs = (
          f'      {{\n'
          f'        "id": {json.dumps(ver.get("id",""))}, "name":'
          f' {json.dumps(ver.get("name",""))}, "quality":'
          f' {json.dumps(ver.get("quality",""))}, "source":'
          f' {json.dumps(ver.get("source",""))}, "codec":'
          f' {json.dumps(ver.get("codec",""))}, "resolution":'
          f' {json.dumps(ver.get("resolution",""))}, "audio":'
          f' {json.dumps(ver.get("audio",""))}, "channels":'
          f' {json.dumps(ver.get("channels",""))},\n'
          f'        "stream_url": {json.dumps(v_stream)},\n'
          f'        "specs": {json.dumps(ver.get("specs",{}))}\n'
          f'      }}'
      )
      v_strs.append(vs)
    all_vers = ",\n".join(v_strs)

    m_stream = fix_stream_url(mv.get("stream_url", ""))

    entry = (
        f'  {{\n'
        f'    "id": {json.dumps(mv.get("id",""))},\n'
        f'    "name": {json.dumps(mv.get("name",""))},\n'
        f'    "title": {json.dumps(mv.get("title",""))}, "original_title":'
        f' {json.dumps(mv.get("original_title",""))}, "year": {mv.get("year",'
        " 0)},\n"
        f'    "tmdb_id": {mv.get("tmdb_id", 0)}, "imdb_id":'
        f' {json.dumps(mv.get("imdb_id",""))}, "imdb_url":'
        f' {json.dumps(mv.get("imdb_url",""))}, "rating": {mv.get("rating",'
        " 0)},\n"
        f'    "plot": {json.dumps(mv.get("plot",""))},\n'
        f'    "poster": {json.dumps(mv.get("poster",""))},\n'
        f'    "fanart": {json.dumps(mv.get("fanart",""))},\n'
        f'    "logo": {json.dumps(mv.get("logo",""))},\n'
        f'    "trailer": {json.dumps(mv.get("trailer",{}))},\n'
        f'    "stream_url": {json.dumps(m_stream)},\n'
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
indian_sorted = sorted(
    indian_pool,
    key=lambda x: (
        int(x.get("year") or 0),
        float(x.get("rating") or 0),
    ),
    reverse=True,
)
hollywood_sorted = sorted(
    hollywood_pool,
    key=lambda x: (
        int(x.get("year") or 0),
        float(x.get("rating") or 0),
    ),
    reverse=True,
)

top_indian = indian_sorted[:6]
top_hollywood = hollywood_sorted[:4]

final_selection = top_indian + top_hollywood

os.makedirs(os.path.dirname(TRENDING_OUTPUT_PATH), exist_ok=True)
with open(TRENDING_OUTPUT_PATH, "w", encoding="utf-8") as f:
  f.write(format_18_line(final_selection))

print(
    f"✅ Exact Top 10 Created: {len(top_indian)} Indian Movies +"
    f" {len(top_hollywood)} Hollywood Movies!"
)
