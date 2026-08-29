# -*- coding: utf-8 -*-
import sys
import os
import json
import urllib.parse
import urllib.request
import xbmc
import xbmcgui
import xbmcplugin

ADDON_HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else ""
REPO_RAW = "https://raw.githubusercontent.com/Moinuflix/My-Movies/main/chunks/"

def fetch_json(file_name):
    try:
        url = REPO_RAW + file_name
        req = urllib.request.Request(url, headers={'User-Agent': 'Kodi-MoinuFlix/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        xbmc.log(f"[MoinuFlix] Fetch error {file_name}: {e}", xbmc.LOGERROR)
        return []

def build_url(query):
    return BASE_URL + '?' + urllib.parse.urlencode(query)

def list_root():
    items = [
        ("▶️ Continue Watching", "watched", "https://img.icons8.com/color/96/resume-button.png"),
        ("🔥 Trending Now", "trending", "https://img.icons8.com/color/96/fire-element.png"),
        ("🎬 Movies", "movies", "https://img.icons8.com/color/96/movie.png"),
        ("📺 TV Series", "series", "https://img.icons8.com/color/96/tv-show.png"),
        ("🎵 5.1 & Atmos Songs", "songs", "https://img.icons8.com/color/96/musical-notes.png"),
        ("🍿 YouTube Vault", "vault_folders", "https://img.icons8.com/color/96/youtube-play.png")
    ]
    for title, action, icon in items:
        li = xbmcgui.ListItem(label=title)
        li.setArt({'icon': icon, 'thumb': icon})
        url = build_url({'action': action})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_movies_from_data(data):
    for m in data:
        title = m.get("title") or m.get("name", "Unknown")
        poster = m.get("poster") or m.get("thumbnail", "")
        stream = m.get("stream_url", "")
        if not stream and m.get("versions"):
            stream = m["versions"][0].get("stream_url", "")
        li = xbmcgui.ListItem(label=title)
        li.setArt({'poster': poster, 'thumb': poster, 'fanart': m.get("fanart", "")})
        li.setInfo('video', {
            'title': title,
            'plot': m.get("plot", ""),
            'rating': float(m.get("rating", 7.5)),
            'year': int(m.get("year", 2024)) if str(m.get("year", "")).isdigit() else 2024
        })
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=stream, listitem=li, isFolder=False)
    xbmcplugin.setContent(ADDON_HANDLE, 'movies')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_watched():
    list_movies_from_data(fetch_json("watched.json"))

def list_trending():
    list_movies_from_data(fetch_json("trending.json"))

def list_movies():
    list_movies_from_data(fetch_json("data_c01.json"))

def list_series():
    data = fetch_json("data_c02.json")
    for s in data:
        title = s.get("title") or s.get("name", "Unknown Series")
        poster = s.get("poster", "")
        li = xbmcgui.ListItem(label=title)
        li.setArt({'poster': poster, 'thumb': poster, 'fanart': s.get("fanart", "")})
        li.setInfo('video', {'title': title, 'plot': s.get("plot", "")})
        url = build_url({'action': 'show_episodes', 'series_id': s.get("tmdb_id") or s.get("id")})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def show_episodes(series_id):
    data = fetch_json("data_c02.json")
    target = None
    for s in data:
        if str(s.get("tmdb_id")) == str(series_id) or str(s.get("id")) == str(series_id):
            target = s
            break
    if target and target.get("episodes"):
        for ep in target["episodes"]:
            title = ep.get("title") or ep.get("name", "Episode")
            stream = ep.get("stream_url", "")
            li = xbmcgui.ListItem(label=title)
            li.setArt({'poster': target.get("poster", ""), 'thumb': target.get("poster", ""), 'fanart': target.get("fanart", "")})
            li.setInfo('video', {'title': title, 'plot': ep.get("plot", "")})
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=stream, listitem=li, isFolder=False)
    xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_songs():
    list_movies_from_data(fetch_json("data_c03.json"))

# --- YOUTUBE VAULT FOLDERS ---
def list_vault_folders():
    categories = [
        ("🔴 24x7 Live News", "🔴 Live News 24x7", "https://img.icons8.com/color/96/news.png"),
        ("😂 Comedy Scenes", "😂 Comedy Scenes", "https://img.icons8.com/color/96/comedy.png"),
        ("🔥 Action & Mass Scenes", "🔥 Action & Mass Scenes", "https://img.icons8.com/color/96/action.png"),
        ("🎵 4K Video Songs", "🎵 4K Video Songs", "https://img.icons8.com/color/96/musical-notes.png"),
        ("🎬 Trailers & Teasers", "🎬 Trailers & Teasers", "https://img.icons8.com/color/96/trailer.png")
    ]
    for label, cat_key, icon in categories:
        li = xbmcgui.ListItem(label=label)
        li.setArt({'icon': icon, 'thumb': icon})
        url = build_url({'action': 'vault_items', 'category': cat_key})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_vault_items(selected_category):
    data = fetch_json("data_c04.json")
    for v in data:
        cat = v.get("category", "")
        # Match exact category or fallback
        if cat == selected_category or (selected_category in cat):
            title = v.get("title", "Video")
            thumb = v.get("thumbnail", "")
            stream = v.get("stream_url", "")
            li = xbmcgui.ListItem(label=title)
            li.setArt({'poster': thumb, 'thumb': thumb})
            li.setInfo('video', {'title': title})
            li.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=stream, listitem=li, isFolder=False)
    xbmcplugin.setContent(ADDON_HANDLE, 'videos')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')
    if not action:
        list_root()
    elif action == 'watched':
        list_watched()
    elif action == 'trending':
        list_trending()
    elif action == 'movies':
        list_movies()
    elif action == 'series':
        list_series()
    elif action == 'show_episodes':
        show_episodes(params.get('series_id'))
    elif action == 'songs':
        list_songs()
    elif action == 'vault_folders':
        list_vault_folders()
    elif action == 'vault_items':
        list_vault_items(params.get('category', ''))

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else "")
