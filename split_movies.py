import json
import os

CHUNKS_DIR = "chunks"
INPUT_FILE = os.path.join(CHUNKS_DIR, "data_c01.json")

if not os.path.exists(INPUT_FILE):
    print("Error: data_c01.json nahi mila!")
    exit(1)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    movies = json.load(f)

total_movies = len(movies)
print(f"=== Total Movies: {total_movies} ===")

tamil = []
telugu = []
hindi = []
english = []

for m in movies:
    orig = str(m.get("original_language") or m.get("orig_lang") or "").lower().strip()
    lang = str(m.get("language") or "").lower().strip()
    ind = str(m.get("industry") or "").lower().strip()
    
    audios = []
    if isinstance(m.get("audio"), list):
        audios = [str(a).lower().strip() for a in m.get("audio")]
    elif isinstance(m.get("audio"), str):
        audios = [m.get("audio").lower().strip()]
        
    specs_audio = str((m.get("specs") or {}).get("audio", "")).lower()

    # 1. Kollywood (Tamil)
    if orig in ["ta", "tam"] or "tamil" in lang or "kollywood" in ind or any("tam" in a for a in audios) or "tam" in specs_audio:
        tamil.append(m)
    # 2. Tollywood (Telugu)
    elif orig in ["te", "tel"] or "telugu" in lang or "tollywood" in ind or any("tel" in a for a in audios) or "tel" in specs_audio:
        telugu.append(m)
    # 3. Bollywood (Hindi)
    elif orig in ["hi", "hin"] or "hindi" in lang or "bollywood" in ind or any("hin" in a for a in audios) or "hin" in specs_audio:
        hindi.append(m)
    # 4. Hollywood (English)
    elif orig in ["en", "eng"] or "english" in lang or "hollywood" in ind or any("eng" in a for a in audios) or "eng" in specs_audio:
        english.append(m)
    else:
        # Agar language tag na mile toh title check karega
        t = (m.get("title") or "").lower()
        if "tamil" in t:
            tamil.append(m)
        elif "telugu" in t:
            telugu.append(m)
        elif "hindi" in t:
            hindi.append(m)
        else:
            english.append(m)

files_map = {
    "data_c01_tamil.json": tamil,
    "data_c01_telugu.json": telugu,
    "data_c01_hindi.json": hindi,
    "data_c01_english.json": english
}

for fname, data in files_map.items():
    out_path = os.path.join(CHUNKS_DIR, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

split_total = len(tamil) + len(telugu) + len(hindi) + len(english)
print(f"Tamil: {len(tamil)} | Telugu: {len(telugu)} | Hindi: {len(hindi)} | English: {len(english)}")
print(f"Total Categorized: {split_total} / {total_movies}")

if split_total == total_movies:
    print("SUCCESS: 0 Missing! Sab barabar hai.")
else:
    print(f"Warning: {total_movies - split_total} movies missing!")
