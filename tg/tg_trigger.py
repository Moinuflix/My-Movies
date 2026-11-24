# MoinuFlix — Telegram BIN Channel Auto-Trigger & Stealth Masker
# Target Folder: Moinuflix/My-Movies/resources/data/tg/
# Colab Run: !pip install -q pyrogram tgcrypto

import os, re, time, uuid, json, base64, asyncio, urllib.request
from pyrogram import Client

API_ID = int(os.environ.get("TG_API_ID") or input("1. Enter TG_API_ID: ").strip())
API_HASH = os.environ.get("TG_API_HASH") or input("2. Enter TG_API_HASH: ").strip()
BIN_CHANNEL = int(os.environ.get("TG_BIN_CHANNEL") or input("3. Private BIN Channel ID (-100...): ").strip())
GH_TOKEN = os.environ.get("GH_TOKEN") or input("4. GitHub PAT Token (ghp_...): ").strip()
SCAN_LIMIT = int(os.environ.get("SCAN_LIMIT") or input("5. Last kitne messages scan karne hain (default 20): ").strip() or "20")

GH_REPO = "Moinuflix/My-Movies"
FOLDER_PATH = "resources/data/tg"

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
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
            return json.loads(base64.b64decode(d["content"]).decode("utf-8")), d["sha"]
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
    urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="PUT"), timeout=20)

async def run_tg_trigger():
    step1, s1_sha = gh_read("step1_pending.json", [])
    step2, _ = gh_read("step2_data_archive.json", {"Data": []})

    # Duplicate check against both Step 1 and Step 2 ("Data")
    known_ids = {str(x.get("tg_msg_id")) for x in step1} | {str(x.get("tg_msg_id")) for x in step2.get("Data", [])}
    added = 0

    async with Client("moinu_tg_vault_session", api_id=API_ID, api_hash=API_HASH) as app:
        async for msg in app.get_chat_history(BIN_CHANNEL, limit=SCAN_LIMIT):
            media = msg.video or msg.document
            if not media:
                continue

            msg_id_str = str(msg.id)
            if msg_id_str in known_ids:
                continue

            raw_name = getattr(media, "file_name", None) or (msg.caption or "").strip()
            if not raw_name or raw_name.startswith("u-t-s-"):
                continue

            size_bytes = getattr(media, "file_size", 0) or 0
            # Skip > 4 GB & split parts
            if size_bytes > 4 * (1024 ** 3) or raw_name.lower().endswith((".001", ".002", ".zip")):
                continue

            size_gb = f"{round(size_bytes / (1024 ** 3), 2)} GB" if size_bytes else "N/A"
            stealth_id = make_stealth_id()
            clean_name = format_clean_name(raw_name, "@ttt")

            # Mask caption inside Telegram BIN Channel
            try:
                await app.edit_message_caption(BIN_CHANNEL, msg.id, stealth_id)
            except Exception as e:
                print(f"⚠️ Caption edit note (#{msg_id_str}): {e}")

            step1.insert(0, {
                "tg_msg_id": msg_id_str,
                "size_gb": size_gb,
                "old_name": raw_name,
                "new_name": clean_name,
                "stealth_name": stealth_id,
                "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            })
            known_ids.add(msg_id_str)
            added += 1
            print(f"✅ TG #{msg_id_str} ({size_gb}) Masked -> {stealth_id}")
            print(f"   🎬 Clean Name -> {clean_name}")
            await asyncio.sleep(1.2)

    if added > 0:
        gh_write("step1_pending.json", step1, s1_sha, f"TG Trigger: Added {added} items to Step 1")
        print(f"\n🚀 Successfully pushed {added} items to {FOLDER_PATH}/step1_pending.json!")
    else:
        print("\n✅ Koi naya unmasked file nahi mila.")

if __name__ == "__main__":
    asyncio.run(run_tg_trigger())
