import os, re, time, uuid, json, base64, urllib.request, urllib.error

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "").strip()
BIN_CHANNEL_ID = str(os.environ.get("TG_BIN_CHANNEL", "")).strip()
GH_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GH_REPO = os.environ.get("GITHUB_REPOSITORY", "Moinuflix/My-Movies").strip()
FOLDER_PATH = "tg"

def make_stealth_id():
    return f"u-t-s-{int(time.time() * 1000)}-e-n-d-{uuid.uuid4().hex[:12]}"

def format_clean_name(raw_name, tag="@ttt"):
    clean = re.sub(r"^(?:www\.[^\s\-]+\s*-\s*|@[^\s\-]+\s*-\s*)", "", raw_name.strip(), flags=re.I)
    clean = re.sub(r"\.(mkv|mp4|avi|webm)$", "", clean, flags=re.I).strip()
    ym = re.search(r"\b(19\d\d|20\d\d)\b", clean)
    title = clean[:ym.start()].strip(" -._") if ym else clean
    year = ym.group(1) if ym else "2026"
    rest = clean[ym.end():].strip(" -._") if ym else ""

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
            for sub in re.split(r"\s+-\s+|\s{2,}", part):
                sub = sub.strip(" -._[]()")
                if not sub or sub == "+":
                    continue
                if re.fullmatch(r"HEVC\s+10bit", sub, flags=re.I):
                    tokens.extend(["[HEVC]", "[10bit]"])
                else:
                    tokens.append(f"[{sub}]")
    if tag:
        tokens.append(f"[{tag}]")
    return f"{title} ({year}) {' '.join(tokens)}.mkv"

def gh_read(file_name, fallback):
    url = f"https://api.github.com/repos/{GH_REPO}/contents/{FOLDER_PATH}/{file_name}"
    headers = {"Authorization": f"Bearer {GH_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            d = json.loads(r.read().decode("utf-8"))
            return json.loads(base64.b64decode(d["content"]).decode("utf-8")), d["sha"]
    except Exception as e:
        print(f"ℹ️ gh_read ({file_name}): {e}")
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
    urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="PUT"), timeout=30)

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
            print(f"⚠️ TG API ({method}) attempt {attempt}/{retries} failed: {e}")
            if attempt == retries:
                raise
            time.sleep(3 * attempt)

def main():
    if not BOT_TOKEN:
        raise RuntimeError("TG_BOT_TOKEN secret missing!")

    print("1️⃣ Clearing any old webhook & verifying Bot...")
    tg_api("deleteWebhook", {"drop_pending_updates": False})
    me = tg_api("getMe")
    print(f"🤖 Connected Bot: @{me.get('result', {}).get('username')}")

    print("2️⃣ Reading GitHub vault state...")
    step1, s1_sha = gh_read("step1_pending.json", [])
    step2, _ = gh_read("step2_data_archive.json", {"Data": []})
    state, st_sha = gh_read("bot_offset.json", {"offset": 0})

    known_ids = {str(x.get("tg_msg_id")) for x in step1} | {str(x.get("tg_msg_id")) for x in step2.get("Data", [])}
    offset = int(state.get("offset", 0))

    print(f"3️⃣ Fetching Telegram updates (offset={offset})...")
    updates = tg_api("getUpdates", {"offset": offset + 1, "limit": 100, "timeout": 5, "allowed_updates": ["channel_post", "message"]})
    if not updates.get("ok"):
        raise RuntimeError(f"Telegram API Error: {updates}")

    results = updates.get("result", [])
    print(f"📩 Total updates received: {len(results)}")

    added = 0
    max_update_id = offset

    for upd in results:
        max_update_id = max(max_update_id, int(upd["update_id"]))
        post = upd.get("channel_post") or upd.get("message")
        if not post:
            continue

        chat_id = str(post.get("chat", {}).get("id", ""))
        print(f"   • Post #{post.get('message_id')} from chat_id={chat_id}")
        if BIN_CHANNEL_ID and chat_id != BIN_CHANNEL_ID:
            continue

        media = post.get("video") or post.get("document")
        if not media:
            continue

        msg_id = str(post["message_id"])
        if msg_id in known_ids:
            continue

        raw_name = media.get("file_name") or (post.get("caption") or "").split("\n")[0].strip()
        if not raw_name or raw_name.startswith("u-t-s-"):
            continue

        size_bytes = int(media.get("file_size") or 0)
        if size_bytes > 4 * (1024 ** 3) or raw_name.lower().endswith((".001", ".002", ".zip")):
            continue

        size_gb = f"{round(size_bytes / (1024 ** 3), 2)} GB" if size_bytes else "N/A"
        stealth_id = make_stealth_id()
        clean_name = format_clean_name(raw_name, "@ttt")

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
            "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
        known_ids.add(msg_id)
        added += 1
        print(f"✅ TG #{msg_id} ({size_gb}) Masked -> {stealth_id}")

    if max_update_id > offset:
        gh_write("bot_offset.json", {"offset": max_update_id}, st_sha, f"Update TG offset: {max_update_id}")

    if added > 0:
        gh_write("step1_pending.json", step1, s1_sha, f"GitHub Action: Added {added} TG items to Step 1")
        print(f"🚀 Pushed {added} items to tg/step1_pending.json!")
    else:
        print("✅ Done — no new unmasked channel posts to add.")

if __name__ == "__main__":
    main()
