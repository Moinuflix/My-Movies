import os, re, time, uuid, json, base64, urllib.request, urllib.parse

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
BIN_CHANNEL_ID = str(os.environ.get("TG_BIN_CHANNEL", "")).strip()
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GH_REPO = os.environ.get("GITHUB_REPOSITORY", "Moinuflix/My-Movies").strip()
TMDB_KEY = "051ccf72e026820cb53b8b8531b6a2ba"
PENDING_PATH = "resources/data/pending_movies.json"
CATALOG_PATH = "resources/data/catalog.json"

KIDS_REGEX = re.compile(
    r"\b(motu\s*patlu|voot\s*kids|chhota\s*bheem|doraemon|shinchan|shin\s*chan|oggy|pokemon|ben\s*10|tom\s*and\s*jerry|peppa\s*pig|paw\s*patrol|rudra|little\s*singham|shiva|balveer|nickelodeon|nick|pogo|cartoon|disney\s*junior|kids)\b",
    re.I
)

def make_stealth_id():
    return f"u-t-s-{int(time.time() * 1000)}-e-n-d-{uuid.uuid4().hex[:12]}"

def extract_clean_title_year(raw_name):
    s = re.sub(r"\.(mkv|mp4|avi|webm|ts)$", "", raw_name.strip(), flags=re.I)
    s = s.replace("_", " ").replace(".", " ")
    s = re.sub(r"^(?:www\.[^\s\-]+\s*-\s*|@[\w\d]+\s*[-:|]?\s*|copy\s+of\s+)+", "", s, flags=re.I).strip(" :-")

    ym = re.search(r"\b(19\d\d|20\d\d)\b", s)
    if ym:
        raw_title, year, rest = s[:ym.start()], ym.group(1), s[ym.end():]
    else:
        tm = re.search(r"\b(2160p|1080p|720p|480p|s\d{1,2}e\d{1,2}|web[-\s]?dl|bluray|hdrip)\b", s, flags=re.I)
        raw_title = s[:tm.start()] if tm else s
        year = "2026"
        rest = s[tm.end():] if tm else ""

    title = re.sub(r"\s+", " ", re.sub(r"[-()\[\]:]+", " ", raw_title)).strip()
    return (title or "Untitled Release"), year, rest.strip(" -")

def format_clean_name(raw_name, is_kids=False, tag="@ttt"):
    title, year, rest = extract_clean_title_year(raw_name)
    tokens = ["[Kids]"] if is_kids else []
    for sub in re.split(r"\s+-\s+|\s{2,}|[\[\]()]", rest):
        sub = sub.strip(" -[]()")
        if sub and sub != "+" and sub.lower() != "copy":
            tokens.append(f"[{sub}]")
    if tag:
        tokens.append(f"[{tag}]")
    return f"{title} ({year}) {' '.join(tokens)}.mkv"

def auto_fetch_tmdb(title, year):
    if not title or title == "Untitled Release":
        return {"tmdb_id": 0, "media_type": "movie", "poster": "", "candidates": []}
    try:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_KEY}&query={urllib.parse.quote(title)}&include_adult=false"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "MoinuFlix/1.0"}), timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
            results = [x for x in data.get("results", []) if x.get("media_type") in ("movie", "tv")]
            if not results:
                return {"tmdb_id": 0, "media_type": "movie", "poster": "", "candidates": []}
            top = results[0]
            candidates = [{
                "tmdb_id": c.get("id", 0),
                "media_type": c.get("media_type", "movie"),
                "title": c.get("title") or c.get("name") or title,
                "year": (c.get("release_date") or c.get("first_air_date") or year)[:4],
                "poster": f"https://image.tmdb.org/t/p/w500{c['poster_path']}" if c.get("poster_path") else ""
            } for c in results[:5]]
            return {
                "tmdb_id": top.get("id", 0),
                "media_type": top.get("media_type", "movie"),
                "poster": f"https://image.tmdb.org/t/p/w780{top['poster_path']}" if top.get("poster_path") else "",
                "candidates": candidates
            }
    except Exception:
        return {"tmdb_id": 0, "media_type": "movie", "poster": "", "candidates": []}

def gh_read(path, fallback):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{path}"
    headers = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
            txt = base64.b64decode(d["content"]).decode("utf-8").strip()
            return (json.loads(txt) if txt else fallback), d["sha"]
    except Exception:
        return fallback, None

def gh_write(path, obj, sha, msg):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{path}"
    headers = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"}
    body = {"message": msg, "content": base64.b64encode(json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")).decode("utf-8"), "branch": "main"}
    if sha:
        body["sha"] = sha
    urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="PUT"), timeout=30)

def tg_api(method, payload=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8") if payload else None, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    if not BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN missing!")

    tg_api("deleteWebhook", {"drop_pending_updates": False})
    pending, p_sha = gh_read(PENDING_PATH, [])
    catalog, _ = gh_read(CATALOG_PATH, {"movies": []})
    if not isinstance(pending, list):
        pending = []

    known_ids = {str(x.get("tg_msg_id") or x.get("id")) for x in pending} | {str(x.get("id")) for x in catalog.get("movies", [])}
    updates = tg_api("getUpdates", {"limit": 100, "timeout": 5, "allowed_updates": ["channel_post", "message"]})
    results = updates.get("result", [])

    added = 0
    max_upd = 0
    for upd in results:
        max_upd = max(max_upd, int(upd["update_id"]))
        post = upd.get("channel_post") or upd.get("message")
        if not post:
            continue
        chat_id = str(post.get("chat", {}).get("id", ""))
        if BIN_CHANNEL_ID and chat_id != BIN_CHANNEL_ID:
            continue
        media = post.get("video") or post.get("document")
        if not media:
            continue

        msg_id = str(post["message_id"])
        if msg_id in known_ids:
            continue

        cap_line = (post.get("caption") or "").split("\n")[0].strip()
        raw_name = media.get("file_name") or ("" if cap_line.startswith("u-t-s-") else cap_line)
        if not raw_name:
            raw_name = f"Telegram_Release_{msg_id}.mkv"

        size_bytes = int(media.get("file_size") or 0)
        if size_bytes > 4 * (1024 ** 3) or raw_name.lower().endswith((".001", ".002", ".zip")):
            continue

        size_gb = f"{round(size_bytes / (1024 ** 3), 2)} GB" if size_bytes else "N/A"
        stealth_id = cap_line if cap_line.startswith("u-t-s-") else make_stealth_id()
        clean_title, year, _ = extract_clean_title_year(raw_name)
        is_kids = bool(KIDS_REGEX.search(f"{raw_name} {clean_title}"))
        clean_name = format_clean_name(raw_name, is_kids=is_kids, tag="@ttt")
        tmdb_info = auto_fetch_tmdb(clean_title, year)

        if not cap_line.startswith("u-t-s-"):
            try:
                tg_api("editMessageCaption", {"chat_id": chat_id, "message_id": int(msg_id), "caption": stealth_id})
            except Exception:
                pass

        pending.insert(0, {
            "source_type": "telegram",
            "tg_msg_id": msg_id,
            "stealth_name": stealth_id,
            "original_filename": raw_name,
            "new_name": clean_name,
            "file_size_gb": size_gb,
            "is_kids": is_kids,
            "tags": ["Kids"] if is_kids else [],
            "tmdb_id": tmdb_info["tmdb_id"],
            "media_type": tmdb_info["media_type"],
            "poster": tmdb_info["poster"],
            "tmdb_candidates": tmdb_info["candidates"],
            "parsed": {
                "title": clean_title,
                "year": year,
                "source": "Telegram",
                "resolution": "1080p" if "1080" in raw_name else "720p"
            }
        })
        known_ids.add(msg_id)
        added += 1
        print(f"✅ Added TG #{msg_id} ({size_gb}) | Kids={is_kids} | {clean_name}")

    if added > 0:
        gh_write(PENDING_PATH, pending, p_sha, f"TG Auto-Sync: Added {added} items to pending_movies.json")

    if max_upd > 0:
        tg_api("getUpdates", {"offset": max_upd + 1, "limit": 1})

if __name__ == "__main__":
    main()
