import json
import urllib.request
import os

MAIN_DATA_PATH = "chunks/data_c01.json"
TRENDING_OUTPUT_PATH = "chunks/trending.json"
SIMKL_CLIENT_ID = "56fea6c62198dd45fa41015d7203fdf29978c5ff2b92f18ff86f0ce33d85f3a8"

def fetch_simkl_trending():
    print("📡 Fetching live Trending Movies from SIMKL API...")
    url = f"https://api.simkl.com/movies/trending?extended=full&client_id={SIMKL_CLIENT_ID}&app-name=MoinuFlix&app-version=1.0"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MoinuFlix/1.0"
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as res:
            data = json.loads(res.read().decode("utf-8"))
            return data
    except Exception as e:
        print(f"⚠️ SIMKL API error: {e}")
        return []

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

local_tmdb_map = {}
local_title_map = {}
for m in my_movies:
    if m.get("tmdb_id"):
        local_tmdb_map[int(m["tmdb_id"])] = m
    t_clean = str(m.get("title", "")).lower().strip()
    if t_clean:
        local_title_map[t_clean] = m

simkl_trending = fetch_simkl_trending()
trending_selection = []
matched_ids = set()

for item in simkl_trending:
    t_ids = item.get("ids", {})
    tmdb_id = t_ids.get("tmdb")
    title = str(item.get("title", "")).lower().strip()

    matched_movie = None
    if tmdb_id and int(tmdb_id) in local_tmdb_map:
        matched_movie = local_tmdb_map[int(tmdb_id)]
    elif title in local_title_map:
        matched_movie = local_title_map[title]

    if matched_movie:
        m_id = matched_movie.get("id") or matched_movie.get("tmdb_id")
        if m_id not in matched_ids:
            trending_selection.append(matched_movie)
            matched_ids.add(m_id)

    if len(trending_selection) >= 10:
        break

if len(trending_selection) < 10:
    sorted_by_rating = sorted(my_movies, key=lambda x: float(x.get("rating") or 0), reverse=True)
    for m in sorted_by_rating:
        m_id = m.get("id") or m.get("tmdb_id")
        if m_id not in matched_ids:
            trending_selection.append(m)
            matched_ids.add(m_id)
        if len(trending_selection) >= 10:
            break

os.makedirs(os.path.dirname(TRENDING_OUTPUT_PATH), exist_ok=True)
with open(TRENDING_OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(format_18_line(trending_selection))

print(f"✅ Created {TRENDING_OUTPUT_PATH} with {len(trending_selection)} items.")
