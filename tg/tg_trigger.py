import os, re, time, uuid, json, base64, urllib.request, urllib.parse, urllib.error

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
BIN_CHANNEL_ID = str(os.environ.get("TG_BIN_CHANNEL", "")).strip()
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GH_REPO = os.environ.get("GITHUB_REPOSITORY", "Moinuflix/My-Movies").strip()
TMDB_KEY = "051ccf72e026820cb53b8b8531b6a2ba"
FOLDER_PATH = "tg"

def make_stealth_id():
    return f"u-t-s-{int(time.time() * 1000)}-e-n-d-{uuid.uuid4().hex[:12]}"

def extract_clean_title_year(raw_name):
    clean = re.sub(r"^(?:www\.[^\s\-]+\s*-\s*|@[^\s\-]+\s*-\s*)", "", raw_name.strip(), flags=re.I)
    clean = re.sub(r"@[\w\d_-]+", "", clean)
    clean = re.sub(r"\.(mkv|mp4|avi|webm|ts)$", "", clean, flags=re.I).strip()
    ym = re.search(r"\b(19\d\d|20\d\d)\b", clean)
    raw_title = clean[:ym.start()] if ym else clean
    title = re.sub(r"[-_.()\[\]]+", " ", raw_title).strip()
    title = re.sub(r"\s+", " ", title)
    year = ym.group(1) if ym else "2026"
    return title, year, (clean[ym.end():].strip(" -._") if ym else "")

def format_clean_name(raw_name, tag="@ttt"):
    title, year, rest = extract_clean_title_year(raw_name)
    tokens = []
    for part in re.split(r"(\[[^\]]+\]|\([^\)]+\))", rest):
        part = part.strip(" -._]")
        if not part or part == "+":
            continue
        if (part.startswith("[") and part.endswith("]")) or (part.startswith("(") and part.endswith(")")):
            inner = part[1:-1].strip()
            if inner:
                tokens.append(f"[{inner}]")
        else:
            for sub in re.split(r"\s+-\s+|\s{2,}|_", part):
                sub = sub.strip(" -._[]()")
                if not sub or sub == "+":
                    continue
                tokens.append(f"[{sub}]")
    if tag:
        tokens.append(f"[{tag}]")
    return f"{title} ({year}) {' '.join(tokens)}.mkv"

def auto_fetch_tmdb(title, year):
    if not title:
        return {"tmdb_id": 0, "poster": "", "candidates": []}
    try:
        q = urllib.parse.quote(title)
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_KEY}&query={q}&include_adult=false"
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "MoinuFlix/1.0"}), timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
            results = [x for x in data.get("results", []) if x.get("media_type") in ("movie", "tv")]
            if not results:
                return {"tmdb_id": 0, "poster": "", "candidates": []}
            top = results[0]
            candidates = []
            for c in results[:4]:
                c_title = c.get("title") or c.get("name") or title
                c_date = c.get("release_date") or c.get("first_air_date") or ""
                candidates.append({
                    "tmdb_id": c.get("id", 0),
                    "title": c_title,
                    "year": c_date[:4] if c_date else year,
                    "poster": f"https://image.tmdb.org/t/p/w500{c['poster_path']}" if c.get("poster_path") else ""
                })
            return {
                "tmdb_id": top.get("id", 0),
                "poster": f"https://image.tmdb.org/t/p/w780{top['poster_path']}" if top.get("poster_path") else "",
                "candidates": candidates
            }
    except Exception as e:
        print(f"⚠️ TMDb auto-fetch note ({title}): {e}")
        return {"tmdb_id": 0, "poster": "", "candidates": []}

def gh_read(file_name, fallback):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{FOLDER_PATH}/{file_name}"
    headers = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
            raw_txt = base64.b64decode(d["content"]).decode("utf-8").strip()
            return (json.loads(raw_txt) if raw_txt else fallback), d["sha"]
    except Exception:
        return fallback, None

def gh_write(file_name, obj, sha, msg):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{FOLDER_PATH}/{file_name}"
    headers = {
        "Authorization": f"Bearer {GH_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    body = {
        "message": msg,
        "content": base64.b64encode(json.dumps(obj, indent=2, ensure_ascii=False).encode("utf-8")).decode("utf-8"),
        "branch": "main"
    }
    if sha:
        body["sha"] = sha
    with urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="PUT"), timeout=30) as r:
        print(f"✅ GitHub Saved: {FOLDER_PATH}/{file_name} (HTTP {r.status})")

def tg_api(method, payload=None, retries=3):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8") if payload else None,
                headers={"Content-Type": "application/json", "User-Agent": "MoinuFlix-Vault/1.0"}
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if attempt == retries:
                raise
            time.sleep(3 * attempt)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN secret missing!")

    tg_api("deleteWebhook", {"drop_pending_updates": False})
    step1, s1_sha = gh_read("step1_pending.json", [])
    step2, _ = gh_read("step2_data_archive.json", {"Data": []})
    state, st_sha = gh_read("bot_offset.json", {"offset": 0})

    if not isinstance(step1, list):
        step1 = []

    known_ids = {str(x.get("tg_msg_id")) for x in step1} | {str(x.get("tg_msg_id")) for x in step2.get("Data", [])}
    offset = int(state.get("offset", 0))

    updates = tg_api("getUpdates", {"offset": offset + 1, "limit": 100, "timeout": 5, "allowed_updates": ["channel_post", "message"]})
    results = updates.get("result", [])
    print(f"📩 Updates fetched: {len(results)}")

    added = 0
    max_update_id = offset

    for upd in results:
        max_update_id = max(max_update_id, int(upd["update_id"]))
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
        clean_name = format_clean_name(raw_name, "@ttt")
        tmdb_info = auto_fetch_tmdb(clean_title, year)

        if not cap_line.startswith("u-t-s-"):
            try:
                tg_api("editMessageCaption", {"chat_id": chat_id, "message_id": int(msg_id), "caption": stealth_id})
            except Exception as e:
                print(f"⚠️ Caption mask note (#{msg_id}): {e}")

        step1.insert(0, {
            "tg_msg_id": msg_id,
            "size_gb": size_gb,
            "old_name": raw_name,
            "new_name": clean_name,
            "stealth_name": stealth_id,
            "tmdb_id": tmdb_info["tmdb_id"],
            "poster": tmdb_info["poster"],
            "tmdb_candidates": tmdb_info["candidates"],
            "parsed": {"title": clean_title, "year": year},
            "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
        known_ids.add(msg_id)
        added += 1
        print(f"✅ TG #{msg_id} ({size_gb}) | TMDb: {tmdb_info['tmdb_id']} | {clean_name}")

    if added > 0:
        gh_write("step1_pending.json", step1, s1_sha, f"TG Vault: Auto-added {added} items with TMDb")

    if max_update_id > offset:
        gh_write("bot_offset.json", {"offset": max_update_id}, st_sha, f"TG Vault: Offset {max_update_id}")

if __name__ == "__main__":
    main()
