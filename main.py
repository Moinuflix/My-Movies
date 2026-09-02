# -*- coding: utf-8 -*-
import sys
import json
import urllib.parse
import urllib.request
import xbmc
import xbmcgui
import xbmcplugin

ADDON_HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else ""
REPO_RAW = "https://raw.githubusercontent.com/Moinuflix/My-Movies/main/chunks/"
ADMIN_PASS = "moinu_secret_2026"
ALLOWED_AGENT = "Kodi-MoinuTV-PrivatePlayer/1.0"

def fetch_json(file_name):
    try:
        url = REPO_RAW + file_name
        req = urllib.request.Request(url, headers={'User-Agent': 'Kodi-MoinuFlix/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        xbmc.log(f"[MoinuFlix] Error fetching {file_name}: {e}", xbmc.LOGERROR)
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
        ("🔴 Live News 24x7", "load_file&file=vault_news.json", "https://img.icons8.com/color/96/news.png"),
        ("😂 Comedy Scenes", "load_file&file=vault_comedy.json", "https://img.icons8.com/color/96/comedy.png"),
        ("🔥 Action & Mass Scenes", "load_file&file=vault_action.json", "https://img.icons8.com/color/96/action.png"),
        ("🎬 Movie Trailers", "load_file&file=vault_trailers.json", "https://img.icons8.com/color/96/trailer.png")
    ]
    for title, action_str, icon in items:
        li = xbmcgui.ListItem(label=title)
        li.setArt({'icon': icon, 'thumb': icon})
        if "load_file" in action_str:
            fname = action_str.split("file=")[1]
            url = build_url({'action': 'load_json', 'file': fname})
        else:
            url = build_url({'action': action_str})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def render_list(data):
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
            'rating': float(m.get("rating", 7.5)) if str(m.get("rating", "")).replace(".","").isdigit() else 7.5,
            'year': int(m.get("year", 2024)) if str(m.get("year", "")).isdigit() else 2024
        })
        li.setProperty('IsPlayable', 'true')
        
        # Click hone par play_media router trigger hoga
        play_url = build_url({'action': 'play_media', 'video_url': stream})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=play_url, listitem=li, isFolder=False)
        
    xbmcplugin.setContent(ADDON_HANDLE, 'movies')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

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
    for s in data:
        if str(s.get("tmdb_id")) == str(series_id) or str(s.get("id")) == str(series_id):
            for ep in s.get("episodes", []):
                title = ep.get("title") or ep.get("name", "Episode")
                stream = ep.get("stream_url", "")
                li = xbmcgui.ListItem(label=title)
                li.setArt({'poster': s.get("poster", ""), 'thumb': s.get("poster", ""), 'fanart': s.get("fanart", "")})
                li.setInfo('video', {'title': title, 'plot': ep.get("plot", "")})
                li.setProperty('IsPlayable', 'true')
                
                play_url = build_url({'action': 'play_media', 'video_url': stream})
                xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=play_url, listitem=li, isFolder=False)
            break
    xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def play_media(video_url):
    if not video_url:
        xbmcgui.Dialog().notification("MoinuFlix", "Stream URL not available", xbmcgui.NOTIFICATION_ERROR)
        xbmcplugin.setResolvedUrl(ADDON_HANDLE, False, xbmcgui.ListItem())
        return

    # GDrive Worker links me password aur User-Agent ensure karein
    if "workers.dev" in video_url:
        clean_url = video_url.split("|")[0]
        if "pass=" not in clean_url:
            separator = "&" if "?" in clean_url else "?"
            clean_url = f"{clean_url}{separator}pass={ADMIN_PASS}"
        video_url = f"{clean_url}|User-Agent={ALLOWED_AGENT}"

    # YouTube Plugin URLs (Vault Categories)
    if "youtube.com" in video_url or "youtu.be" in video_url:
        if "v=" in video_url:
            vid = video_url.split("v=")[1].split("&")[0]
            video_url = f"plugin://plugin.video.youtube/play/?video_id={vid}"

    play_item = xbmcgui.ListItem(path=video_url)
    play_item.setProperty('IsPlayable', 'true')
    play_item.setContentLookup(False)
    
    if "workers.dev" in video_url or video_url.endswith(".mp4"):
        play_item.setMimeType('video/mp4')
        
    xbmcplugin.setResolvedUrl(handle=ADDON_HANDLE, succeeded=True, listitem=play_item)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring))
    action = params.get('action')
    if not action:
        list_root()
    elif action == 'load_json':
        render_list(fetch_json(params.get('file', 'data_c01.json')))
    elif action == 'watched':
        render_list(fetch_json("watched.json"))
    elif action == 'trending':
        render_list(fetch_json("trending.json"))
    elif action == 'movies':
        render_list(fetch_json("data_c01.json"))
    elif action == 'songs':
        render_list(fetch_json("data_c03.json"))
    elif action == 'series':
        list_series()
    elif action == 'show_episodes':
        show_episodes(params.get('series_id'))
    elif action == 'play_media':
        play_media(params.get('video_url'))

if __name__ == '__main__':
    router(sys.argv[2][1:] if len(sys.argv) > 2 else "")
