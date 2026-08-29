# -*- coding: utf-8 -*-
import sys
import json
import urllib.request
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin

ADDON_HANDLE = int(sys.argv[1]) if len(sys.argv) > 1 else 0
BASE_URL = sys.argv[0] if len(sys.argv) > 0 else ""
REPO_RAW_BASE = "https://raw.githubusercontent.com/Moinuflix/My-Movies/main/chunks/"
USER_AGENT = "Kodi-MoinuTV-PrivatePlayer/1.0"

def build_url(query):
    return BASE_URL + "?" + urllib.parse.urlencode(query)

def fetch_json(filename):
    url = REPO_RAW_BASE + filename
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=10) as res:
            return json.loads(res.read().decode("utf-8"))
    except Exception as e:
        xbmc.log("[MoinuFlix] Error loading " + filename + ": " + str(e), xbmc.LOGERROR)
        return []

def main_menu():
    categories = [
        ("🎬 Movies", "list_movies"),
        ("📺 Web Series", "list_series"),
        ("🎵 5.1 / Atmos Songs", "list_songs"),
        ("🍿 YouTube Vault", "list_vault"),
        ("🔥 Recently Added", "list_recent"),
        ("⭐ Continue Watching", "list_continue")
    ]
    for title, mode in categories:
        li = xbmcgui.ListItem(label=title)
        url = build_url({"mode": mode})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_movies():
    movies = fetch_json("data_c01.json")
    for m in movies:
        title = m.get("title", m.get("name", "Movie"))
        poster = m.get("poster", "")
        fanart = m.get("fanart", "")
        plot = m.get("plot", "")
        versions = m.get("versions", [])
        
        li = xbmcgui.ListItem(label=title)
        li.setArt({"poster": poster, "thumb": poster, "fanart": fanart})
        li.setInfo("video", {
            "title": title,
            "plot": plot,
            "mediatype": "movie",
            "rating": m.get("rating", 0),
            "year": m.get("year", 2026)
        })

        if len(versions) > 1:
            # Play mode triggers modal popup dialog instead of opening a directory
            li.setProperty("IsPlayable", "true")
            url = build_url({"mode": "play_movie_dialog", "title": title})
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
        elif len(versions) == 1:
            stream = versions[0].get("stream_url", m.get("stream_url", ""))
            li.setProperty("IsPlayable", "true")
            url = build_url({"mode": "play_direct", "url": stream, "title": title, "poster": poster})
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
        else:
            stream = m.get("stream_url", "")
            li.setProperty("IsPlayable", "true")
            url = build_url({"mode": "play_direct", "url": stream, "title": title, "poster": poster})
            xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)

    xbmcplugin.setContent(ADDON_HANDLE, "movies")
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def play_movie_dialog(target_title):
    movies = fetch_json("data_c01.json")
    target_movie = next((m for m in movies if (m.get("title") or m.get("name")) == target_title), None)
    if not target_movie:
        return

    versions = target_movie.get("versions", [])
    if not versions:
        stream = target_movie.get("stream_url", "")
        play_stream(stream, target_title, target_movie.get("poster", ""))
        return

    if len(versions) == 1:
        stream = versions[0].get("stream_url", target_movie.get("stream_url", ""))
        play_stream(stream, target_title, target_movie.get("poster", ""))
        return

    dialog_labels = []
    for v in versions:
        q_label = v.get("quality", v.get("resolution", "HD"))
        audio = v.get("audio", "Stereo")
        channels = v.get("channels", "")
        audio_str = f"{audio} {channels}".strip()
        dialog_labels.append(f"{q_label} • {audio_str}")

    dialog = xbmcgui.Dialog()
    selected_index = dialog.select(f"Select Quality - {target_title}", dialog_labels)
    if selected_index >= 0:
        chosen_stream = versions[selected_index].get("stream_url", "")
        play_stream(chosen_stream, target_title, target_movie.get("poster", ""))

def play_stream(stream_url, title, poster=""):
    li = xbmcgui.ListItem(label=title, path=stream_url)
    li.setArt({"poster": poster, "thumb": poster})
    li.setInfo("video", {"title": title, "mediatype": "movie"})
    xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, li)

def list_series():
    shows = fetch_json("data_c02.json")
    for s in shows:
        title = s.get("title", "Series")
        poster = s.get("poster", "")
        fanart = s.get("fanart", "")
        li = xbmcgui.ListItem(label=title)
        li.setArt({"poster": poster, "thumb": poster, "fanart": fanart})
        li.setInfo("video", {"title": title, "plot": s.get("plot", ""), "mediatype": "tvshow"})
        url = build_url({"mode": "episodes", "tmdb_id": str(s.get("tmdb_id", ""))})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=True)
    xbmcplugin.setContent(ADDON_HANDLE, "tvshows")
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_episodes(tmdb_id):
    shows = fetch_json("data_c02.json")
    show = next((s for s in shows if str(s.get("tmdb_id", "")) == str(tmdb_id)), None)
    if not show:
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        return
    episodes = show.get("episodes", [])
    poster = show.get("poster", "")
    fanart = show.get("fanart", "")
    for ep in episodes:
        title = ep.get("title", ep.get("name", "Episode"))
        stream = ep.get("stream_url", "")
        li = xbmcgui.ListItem(label=title)
        li.setArt({"poster": poster, "thumb": poster, "fanart": fanart})
        li.setInfo("video", {"title": title, "plot": ep.get("plot", ""), "mediatype": "episode"})
        li.setProperty("IsPlayable", "true")
        url = build_url({"mode": "play_direct", "url": stream, "title": title, "poster": poster})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
    xbmcplugin.setContent(ADDON_HANDLE, "episodes")
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_songs():
    songs = fetch_json("data_c03.json")
    for s in songs:
        title = s.get("title", "Song")
        poster = s.get("poster", "")
        stream = s.get("stream_url", "")
        li = xbmcgui.ListItem(label=title)
        li.setArt({"thumb": poster, "poster": poster, "fanart": poster})
        li.setInfo("music", {"title": title})
        li.setProperty("IsPlayable", "true")
        url = build_url({"mode": "play_direct", "url": stream, "title": title, "poster": poster})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
    xbmcplugin.setContent(ADDON_HANDLE, "songs")
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_vault():
    vault = fetch_json("data_c04.json")
    for v in vault:
        title = v.get("title", "Clip")
        thumb = v.get("thumbnail", "")
        stream = v.get("stream_url", "")
        li = xbmcgui.ListItem(label=title)
        li.setArt({"thumb": thumb, "poster": thumb, "fanart": thumb})
        li.setInfo("video", {"title": title})
        li.setProperty("IsPlayable", "true")
        url = build_url({"mode": "play_direct", "url": stream, "title": title, "poster": thumb})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
    xbmcplugin.setContent(ADDON_HANDLE, "videos")
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_recent():
    movies = fetch_json("data_c01.json")
    for m in movies[:15]:
        title = m.get("title", "Movie")
        poster = m.get("poster", "")
        versions = m.get("versions", [])
        stream = versions[0].get("stream_url", m.get("stream_url", "")) if versions else m.get("stream_url", "")
        li = xbmcgui.ListItem(label=title)
        li.setArt({"poster": poster, "thumb": poster})
        li.setInfo("video", {"title": title, "mediatype": "movie"})
        li.setProperty("IsPlayable", "true")
        url = build_url({"mode": "play_direct", "url": stream, "title": title, "poster": poster})
        xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=url, listitem=li, isFolder=False)
    xbmcplugin.setContent(ADDON_HANDLE, "movies")
    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def list_continue():
    list_recent()

if __name__ == "__main__":
    qs = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2].startswith("?") else ""
    params = dict(urllib.parse.parse_qsl(qs))
    mode = params.get("mode")
    if mode == "list_movies": list_movies()
    elif mode == "play_movie_dialog": play_movie_dialog(params.get("title", ""))
    elif mode == "play_direct": play_stream(params.get("url", ""), params.get("title", ""), params.get("poster", ""))
    elif mode == "list_series": list_series()
    elif mode == "episodes": list_episodes(params.get("tmdb_id", ""))
    elif mode == "list_songs": list_songs()
    elif mode == "list_vault": list_vault()
    elif mode == "list_recent": list_recent()
    elif mode == "list_continue": list_continue()
    else: main_menu()
