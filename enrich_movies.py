import json
import urllib.request
import os
import time

TMDB_API_KEY = "051ccf72e026820cb53b8b8531b6a2ba"
JSON_PATH = "chunks/data_c01.json"

if not os.path.exists(JSON_PATH):
    print("File nahi mili:", JSON_PATH)
    exit(1)

with open(JSON_PATH, "r", encoding="utf-8") as f:
    movies = json.load(f)

print(f"Total movies mili: {len(movies)}")

for idx, m in enumerate(movies):
    title = m.get("title", "Unknown")
    tmdb_id = m.get("tmdb_id")

    if not tmdb_id:
        print(f"[{idx+1}/{len(movies)}] Skip: {title} (tmdb_id missing)")
        continue

    print(f"[{idx+1}/{len(movies)}] Processing: {title}...")

    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&append_to_response=credits,videos"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        # 1. Exact Runtime update karega
        if data.get("runtime"):
            m["runtime"] = data.get("runtime")

        # 2. Sirf Director add/update karega
        directors = [
            crew.get("name") 
            for crew in data.get("credits", {}).get("crew", []) 
            if crew.get("job") == "Director"
        ]
        if directors:
            m["director"] = directors

        # 3. Sirf Cast add/update karega
        cast_list = []
        for c in data.get("credits", {}).get("cast", [])[:5]:
            profile_path = c.get("profile_path")
            cast_list.append({
                "name": c.get("name"),
                "role": c.get("character", ""),
                "thumbnail": f"https://image.tmdb.org/t/p/w185{profile_path}" if profile_path else ""
            })
        if cast_list:
            m["cast"] = cast_list

        # 4. TMDB official YouTube link sahi karega
        videos = data.get("videos", {}).get("results", [])
        trailer_key = None
        for v in videos:
            if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser"] and v.get("iso_639_1") == "ta":
                trailer_key = v.get("key")
                break
        if not trailer_key:
            for v in videos:
                if v.get("site") == "YouTube" and v.get("type") in ["Trailer", "Teaser"]:
                    trailer_key = v.get("key")
                    break

        if trailer_key:
            m["trailer"] = f"https://www.youtube.com/watch?v={trailer_key}"

        time.sleep(0.2)

    except Exception as e:
        print(f"Error {title}: {e}")

# Original structure intact rakhte hue save karega
with open(JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(movies, f, indent=2, ensure_ascii=False)

print("\nDone! Bus YouTube link, cast aur director add ho gaye, baaki sab unchanged raha!")
