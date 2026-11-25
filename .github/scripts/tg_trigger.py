<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MoinuFlix — Unified Pending Ingest & Approval Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #080d1a; --card-bg: rgba(15, 23, 42, 0.88); --card-border: rgba(56, 189, 248, 0.22);
      --laser-cyan: #38bdf8; --laser-green: #10b981; --laser-gold: #f59e0b; --laser-red: #ef4444;
      --laser-purple: #a855f7; --text-main: #f8fafc; --text-muted: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
    body { background-color: var(--bg-dark); color: var(--text-main); padding: 1.5rem; min-height: 100vh; }
    .container { max-width: 1350px; margin: 0 auto; }
    .top-header {
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 58, 138, 0.85));
      border: 1px solid var(--card-border); border-radius: 16px; padding: 1.25rem 2rem;
      display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem;
    }
    .brand-title { font-size: 1.35rem; font-weight: 800; color: #fff; }
    .brand-sub { font-size: 0.82rem; color: var(--laser-cyan); margin-top: 3px; font-weight: 600; }
    .nav-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .btn-pill {
      background: rgba(56, 189, 248, 0.12); border: 1px solid var(--laser-cyan); color: #fff;
      padding: 0.5rem 1rem; border-radius: 10px; font-size: 0.82rem; font-weight: 700;
      cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 6px;
    }
    .btn-pill:hover { background: var(--laser-cyan); color: #020617; }
    .btn-green { background: linear-gradient(135deg, var(--laser-green), #059669); color: #fff; border: none; }
    .btn-purple { background: rgba(168, 85, 247, 0.2); border-color: var(--laser-purple); color: #e9d5ff; }
    .stats-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.25rem; }
    .stat-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 14px; padding: 1rem 1.4rem; }
    .stat-lbl { font-size: 0.72rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; }
    .stat-val { font-size: 1.4rem; font-weight: 800; color: #fff; margin-top: 4px; }
    .batch-toolbar {
      display: flex; justify-content: space-between; align-items: center; background: rgba(15, 23, 42, 0.6);
      border: 1px solid var(--card-border); padding: 0.75rem 1.5rem; border-radius: 12px; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 10px;
    }
    .select-all-box { display: inline-flex; align-items: center; gap: 8px; font-size: 0.85rem; font-weight: 700; color: #fff; cursor: pointer; }
    .select-all-box input[type="checkbox"], .card-select-cb { width: 18px; height: 18px; accent-color: var(--laser-green); cursor: pointer; }
    #action-status-banner {
      display: none; padding: 0.85rem 1.5rem; border-radius: 12px; margin-bottom: 1.25rem;
      font-size: 0.85rem; font-weight: 700; background: rgba(56, 189, 248, 0.15); border: 1px solid var(--laser-cyan); color: var(--laser-cyan);
    }
    .pending-list { display: flex; flex-direction: column; gap: 1.25rem; }
    .pending-card {
      background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px;
      padding: 1.25rem; display: flex; gap: 1.25rem; align-items: center;
    }
    .pending-card:hover { border-color: var(--laser-cyan); }
    .poster-preview { width: 85px; height: 125px; border-radius: 8px; object-fit: cover; background: #020617; flex-shrink: 0; }
    .card-content { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 6px; }
    .raw-name-title { font-size: 0.78rem; color: #fca5a5; word-break: break-all; font-family: monospace; }
    .parsed-headline { font-size: 1.15rem; font-weight: 800; color: #fff; }
    .dash-preview-box {
      font-family: monospace; font-size: 0.82rem; color: var(--laser-green);
      background: rgba(2, 6, 23, 0.8); padding: 6px 10px; border-radius: 6px; border: 1px dashed var(--laser-cyan); word-break: break-all;
    }
    .tags-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; margin-top: 4px; }
    .badge { font-size: 0.72rem; font-weight: 700; padding: 2px 8px; border-radius: 6px; background: rgba(255,255,255,0.06); color: #fff; }
    .badge-tg { background: rgba(168, 85, 247, 0.22); color: #e9d5ff; border: 1px solid rgba(168, 85, 247, 0.45); }
    .badge-gdrive { background: rgba(56, 189, 248, 0.2); color: var(--laser-cyan); }
    .badge-kids { background: rgba(245, 158, 11, 0.22); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.5); }
    .badge-size { background: rgba(16, 185, 129, 0.2); color: var(--laser-green); border: 1px solid rgba(16, 185, 129, 0.4); }
    .card-actions { display: flex; flex-direction: column; gap: 8px; flex-shrink: 0; }
    .btn-approve { background: var(--laser-green); color: #020617; border: none; padding: 0.65rem 1.2rem; border-radius: 10px; font-weight: 800; font-size: 0.85rem; cursor: pointer; }
    .btn-edit-form { background: rgba(56, 189, 248, 0.15); border: 1px solid var(--laser-cyan); color: var(--laser-cyan); padding: 0.55rem 1.1rem; border-radius: 10px; font-weight: 700; font-size: 0.8rem; cursor: pointer; }
    .btn-reject { background: transparent; border: 1px solid var(--laser-red); color: var(--laser-red); padding: 0.4rem 0.9rem; border-radius: 10px; font-size: 0.75rem; font-weight: 700; cursor: pointer; }
    .modal-backdrop { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(2, 6, 23, 0.85); backdrop-filter: blur(10px); z-index: 9999; display: none; align-items: center; justify-content: center; padding: 1.5rem; }
    .modal-box { background: #0b1329; border: 1px solid var(--laser-cyan); border-radius: 18px; width: 100%; max-width: 650px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
    .batch-progress-scroll { max-height: 220px; overflow-y: auto; background: #020617; border: 1px solid var(--card-border); border-radius: 10px; padding: 10px; display: flex; flex-direction: column; gap: 6px; font-size: 0.8rem; font-family: monospace; }
    @media (max-width: 850px) { .pending-card { flex-direction: column; align-items: flex-start; } .card-actions { width: 100%; flex-direction: row; justify-content: flex-end; } }
  </style>
</head>
<body>

<div class="container">
  <div class="top-header">
    <div>
      <div class="brand-title">MOINUFLIX — UNIFIED PENDING ARRIVALS</div>
      <div class="brand-sub">Single `resources/data/pending_movies.json` • GDrive + Telegram + Auto-Kids Tag</div>
    </div>
    <div class="nav-actions">
      <button class="btn-pill btn-purple" onclick="triggerWorkflow('tg_vault_sync.yml', 'Telegram Sync')">⚡ Trigger TG Action</button>
      <button class="btn-pill" onclick="triggerWorkflow('scan_drive.yml', 'Drive Scan')">⚡ Trigger Drive Action</button>
      <button class="btn-pill btn-green" onclick="triggerBatchSelectedApproval()">🚀 Approve Selected</button>
      <button class="btn-pill" onclick="loadPendingList()">🔄 Refresh</button>
      <a href="inbox.html" class="btn-pill">📝 Form</a>
      <a href="admin.html" class="btn-pill">🎬 Library</a>
      <button class="btn-pill" onclick="configureToken()">⚙️ Token</button>
    </div>
  </div>

  <div class="stats-strip">
    <div class="stat-card"><div class="stat-lbl">Total Pending Queue</div><div class="stat-val" id="stat-pending-count" style="color:var(--laser-gold);">0</div></div>
    <div class="stat-card"><div class="stat-lbl">Target Storage Chunk (50-Limit)</div><div class="stat-val" id="stat-target-chunk" style="color:var(--laser-cyan);">chunk_01.json</div></div>
    <div class="stat-card"><div class="stat-lbl">Master Catalog Total</div><div class="stat-val" id="stat-catalog-total">0 Movies</div></div>
  </div>

  <div class="batch-toolbar">
    <label class="select-all-box"><input type="checkbox" id="chk-select-all" onchange="toggleSelectAll(this.checked)"><span>Select All In Queue</span></label>
    <div style="font-size:0.8rem; color:var(--text-muted);"><span id="selected-count-label" style="color:var(--laser-cyan); font-weight:800;">0</span> selected</div>
  </div>

  <div id="action-status-banner"></div>
  <div class="pending-list" id="pending-items-container"><div style="color:var(--text-muted); padding:30px; text-align:center;">Loading queue...</div></div>
</div>

<!-- BATCH MODAL -->
<div class="modal-backdrop" id="batch-modal">
  <div class="modal-box" style="max-width:700px;">
    <div style="display:flex; justify-content:space-between; align-items:center;"><strong style="font-size:1.1rem;">🚀 Batch Approval In Progress</strong><button style="background:transparent; border:none; color:#fff; font-size:1.3rem; cursor:pointer;" onclick="closeBatchModal()">✕</button></div>
    <div class="batch-progress-scroll" id="batch-log-container"></div>
    <div style="display:flex; justify-content:flex-end;"><button class="btn-pill" id="btn-batch-done" style="display:none;" onclick="closeBatchModal()">Done</button></div>
  </div>
</div>

<script>
  const TMDB_KEY = "051ccf72e026820cb53b8b8531b6a2ba";
  const GH_REPO = "Moinuflix/My-Movies";
  const GH_BRANCH = "main";
  const WORKER_BASE = "https://gdrive-stream.moinudeentv.workers.dev/?id=";
  const TG_WORKER_BASE = "https://tg-stream.moinudeentv.workers.dev/?msg_id=";
  const USER_AGENT = "|User-Agent=Kodi-MoinuTV-PrivatePlayer/1.0";

  let pendingList = [];
  let catalogCount = 0;
  let currentTargetChunk = "chunk_01.json";

  function getToken() { return (localStorage.getItem("moinuflix_gh_token") || "").trim(); }
  function configureToken() {
    const input = prompt("Enter GitHub Personal Access Token (PAT):", getToken());
    if (input !== null) { localStorage.setItem("moinuflix_gh_token", input.trim()); loadPendingList(); }
  }

  function showStatus(msg, isError = false) {
    const b = document.getElementById("action-status-banner");
    b.style.display = "block";
    b.style.color = isError ? "var(--laser-red)" : "var(--laser-cyan)";
    b.style.borderColor = isError ? "var(--laser-red)" : "var(--laser-cyan)";
    b.textContent = msg;
  }

  async function triggerWorkflow(wf, label) {
    const token = getToken();
    if (!token) return alert("GitHub Token missing!");
    showStatus(`⚡ Running GitHub Action: ${label}...`);
    try {
      const res = await fetch(`https://api.github.com/repos/${GH_REPO}/actions/workflows/${wf}/dispatches`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}`, "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json" },
        body: JSON.stringify({ ref: GH_BRANCH })
      });
      if (res.status === 204 || res.ok) {
        showStatus(`🚀 ${label} started! Auto-refreshing in 18s...`);
        setTimeout(loadPendingList, 18000);
      } else throw new Error((await res.json()).message || "Dispatch failed");
    } catch (e) { showStatus(`❌ ${e.message}`, true); }
  }

  async function loadMasterStats() {
    try {
      const res = await fetch(`https://raw.githubusercontent.com/${GH_REPO}/${GH_BRANCH}/resources/data/catalog.json?t=${Date.now()}`);
      if (res.ok) {
        const cat = await res.json();
        const movies = cat.movies || (Array.isArray(cat) ? cat : []);
        catalogCount = movies.length;
        document.getElementById("stat-catalog-total").textContent = `${catalogCount} Movies`;
        currentTargetChunk = `chunk_${String(Math.floor(catalogCount / 50) + 1).padStart(2, '0')}.json`;
        document.getElementById("stat-target-chunk").textContent = currentTargetChunk;
      }
    } catch (_) {}
  }

  async function loadPendingList() {
    await loadMasterStats();
    const container = document.getElementById("pending-items-container");
    try {
      const res = await fetch(`https://raw.githubusercontent.com/${GH_REPO}/${GH_BRANCH}/resources/data/pending_movies.json?t=${Date.now()}`);
      if (!res.ok) { pendingList = []; }
      else {
        let text = (await res.text()).replace(/\\\[/g, '[').replace(/\\\]/g, ']');
        pendingList = text.trim() ? JSON.parse(text) : [];
      }
      document.getElementById("stat-pending-count").textContent = pendingList.length;
      renderPendingCards();
    } catch (err) {
      container.innerHTML = `<div style="color:var(--laser-red); padding:30px; text-align:center;">Error: ${err.message}</div>`;
    }
  }

  function renderPendingCards() {
    const container = document.getElementById("pending-items-container");
    container.innerHTML = "";
    if (!pendingList.length) {
      container.innerHTML = '<div style="color:var(--laser-green); padding:40px; text-align:center;">🎉 Queue is 100% clear!</div>';
      updateSelectedCount();
      return;
    }

    pendingList.forEach((item, index) => {
      const isTg = item.source_type === "telegram" || Boolean(item.tg_msg_id);
      const isKids = Boolean(item.is_kids) || /motu[\s_.]*patlu|voot[\s_.]*kids|cartoon|kids/i.test(item.original_filename || item.new_name || "");
      // Real raw filename 100% untouched
      const rawName = item.original_filename || item.old_name || "";
      const newCleanName = item.new_name || rawName;
      const title = item.parsed?.title || newCleanName.split("(")[0].trim();
      const year = item.parsed?.year || "2026";
      const size = item.file_size_gb || item.size_gb || "N/A";
      const poster = item.poster || item.tmdb_candidates?.[0]?.poster || "https://via.placeholder.com/90x135?text=No+Poster";

      const card = document.createElement("div");
      card.className = "pending-card";
      card.innerHTML = `
        <div style="padding:0 5px;"><input type="checkbox" class="card-select-cb" data-index="${index}" onchange="updateSelectedCount()"></div>
        <img src="${poster}" class="poster-preview" alt="" onerror="this.src='https://via.placeholder.com/90x135?text=Poster'">
        <div class="card-content">
          <div class="raw-name-title">📁 REAL RAW: ${escapeHtml(rawName)}</div>
          <div class="parsed-headline">${escapeHtml(title)} (${year})</div>
          <div class="dash-preview-box">✨ NEW CLEAN: ${escapeHtml(newCleanName)}</div>
          <div class="tags-row">
            ${isTg ? `<span class="badge badge-tg">⚡ TG #${escapeHtml(item.tg_msg_id)} • 🛡️ ${escapeHtml(item.stealth_name || '')}</span>` : `<span class="badge badge-gdrive">📁 GDrive</span>`}
            ${isKids ? `<span class="badge badge-kids">🧸 Kids</span>` : ''}
            <span class="badge badge-size">💾 ${escapeHtml(size)}</span>
            ${item.tmdb_id ? `<span class="badge">TMDB: ${item.tmdb_id}</span>` : ''}
            <span class="badge" style="color:var(--laser-cyan);">${currentTargetChunk}</span>
          </div>
        </div>
        <div class="card-actions">
          <button class="btn-approve" onclick="approveSingleItem(${index})">✓ Approve</button>
          <button class="btn-edit-form" onclick="sendToEditForm(${index})">✏️ Edit in Form</button>
          <button class="btn-reject" onclick="rejectItem(${index})">✕ Dismiss</button>
        </div>
      `;
      container.appendChild(card);
    });
    updateSelectedCount();
  }

  function toggleSelectAll(c) { document.querySelectorAll(".card-select-cb").forEach(cb => cb.checked = c); updateSelectedCount(); }
  function updateSelectedCount() { document.getElementById("selected-count-label").textContent = document.querySelectorAll(".card-select-cb:checked").length; }
  function closeBatchModal() { document.getElementById("batch-modal").style.display = "none"; loadPendingList(); }

  function sendToEditForm(index) {
    sessionStorage.setItem("moinuflix_edit_pending", JSON.stringify(pendingList[index]));
    window.location.href = "inbox.html?load_pending=1";
  }

  async function triggerBatchSelectedApproval() {
    const checked = Array.from(document.querySelectorAll(".card-select-cb:checked"));
    if (!checked.length) return alert("Select at least 1 item!");
    const logBox = document.getElementById("batch-log-container");
    logBox.innerHTML = "";
    document.getElementById("btn-batch-done").style.display = "none";
    document.getElementById("batch-modal").style.display = "flex";

    for (let idx of checked.map(cb => parseInt(cb.dataset.index, 10)).sort((a, b) => b - a)) {
      const title = pendingList[idx].parsed?.title || pendingList[idx].new_name || "Item";
      const d = document.createElement("div");
      d.textContent = `⏳ Committing: ${title}...`;
      logBox.appendChild(d);
      try { await approveSingleItem(idx, true); d.textContent = `✅ Done: ${title}`; d.style.color = "var(--laser-green)"; }
      catch (e) { d.textContent = `❌ Error: ${e.message}`; d.style.color = "var(--laser-red)"; }
    }
    document.getElementById("btn-batch-done").style.display = "inline-flex";
  }

  async function approveSingleItem(index, isBatch = false) {
    const token = getToken();
    if (!token) return alert("GitHub Token missing!");
    const item = pendingList[index];
    const isTg = item.source_type === "telegram" || Boolean(item.tg_msg_id);
    const sourceType = isTg ? "telegram" : "gdrive";
    const mediaId = isTg ? String(item.tg_msg_id).trim() : String(item.gdrive_id || "").replace(/\s+/g, '');
    const streamUrl = isTg ? `${TG_WORKER_BASE}${mediaId}${USER_AGENT}` : `${WORKER_BASE}${mediaId}${USER_AGENT}`;

    const isKids = Boolean(item.is_kids) || /motu[\s_.]*patlu|voot[\s_.]*kids|cartoon|kids/i.test(item.original_filename || item.new_name || "");
    const title = item.parsed?.title || (item.new_name || "").split("(")[0].trim() || "Movie";
    const year = parseInt(item.parsed?.year || "2026", 10);
    const size = item.file_size_gb || "1.5 GB";
    const finalDashName = item.new_name || `${title} (${year}).mkv`;

    if (!isBatch) showStatus(`⚡ Publishing "${title}" (${sourceType}) to Master Catalog...`);

    let tmdbId = item.selected_tmdb_id || item.tmdb_id || 0;
    let mediaType = item.media_type || "movie";
    let poster = item.poster || "", fanart = "", rating = 7.5, origLang = "hi", genres = isKids ? ["Kids", "Animation"] : ["Drama"], plot = "", cast = [];

    if (tmdbId) {
      try {
        const res = await fetch(`https://api.themoviedb.org/3/${mediaType === "tv" ? "tv" : "movie"}/${tmdbId}?api_key=${TMDB_KEY}&append_to_response=credits`);
        if (res.ok) {
          const td = await res.json();
          poster = td.poster_path ? `https://image.tmdb.org/t/p/w780${td.poster_path}` : poster;
          fanart = td.backdrop_path ? `https://image.tmdb.org/t/p/original${td.backdrop_path}` : poster;
          rating = td.vote_average ? parseFloat(td.vote_average.toFixed(1)) : 7.5;
          origLang = td.original_language || "hi";
          genres = (td.genres || []).map(g => g.name);
          if (isKids && !genres.includes("Kids")) genres.unshift("Kids");
          plot = td.overview || "";
          cast = (td.credits?.cast || []).slice(0, 10).map(c => ({ name: c.name, character: c.character, profile: c.profile_path ? `https://image.tmdb.org/t/p/w185${c.profile_path}` : null }));
        }
      } catch (_) {}
    }

    const targetChunkPath = `resources/data/chunks/${currentTargetChunk}`;
    const catalogPath = `resources/data/catalog.json`;

    // 1. Write to Chunk (50-Limit)
    let chunkData = { chunk_id: currentTargetChunk.replace(".json", ""), movie_count: 0, movies: [] }, chunkSha;
    const cRes = await fetch(`https://api.github.com/repos/${GH_REPO}/contents/${targetChunkPath}?t=${Date.now()}`, { headers: { "Authorization": `token ${token}` } });
    if (cRes.ok) { const cj = await cRes.json(); chunkSha = cj.sha; chunkData = JSON.parse(decodeURIComponent(escape(atob(cj.content)))); }

    const verObj = { id: mediaId, source_type: sourceType, name: finalDashName, quality: "1080p FHD", source: isTg ? "Telegram" : "WEB-DL", size, stream_url: streamUrl };
    chunkData.movies = chunkData.movies || [];
    chunkData.movies.push({
      id: mediaId, source_type: sourceType, is_kids: isKids, tags: isKids ? ["Kids"] : [],
      tmdb_id: Number(tmdbId) || 0, name: finalDashName, title, original_title: title, year, rating,
      original_language: origLang, genres, plot, cast,
      artwork: { poster, fanart, thumbnail: poster },
      stream_url: streamUrl,
      specs: { resolution: "1080p", source: isTg ? "Telegram" : "WEB-DL", audio: "5.1", size },
      versions: [verObj]
    });
    chunkData.movie_count = chunkData.movies.length;
    await commitGithubFile(targetChunkPath, chunkData, `Add (${sourceType}): ${title}`, chunkSha, token);

    // 2. Write to Single Master Catalog with `source_type` line
    let catData = { movies: [] }, catSha;
    const catRes = await fetch(`https://api.github.com/repos/${GH_REPO}/contents/${catalogPath}?t=${Date.now()}`, { headers: { "Authorization": `token ${token}` } });
    if (catRes.ok) { const ctJ = await catRes.json(); catSha = ctJ.sha; catData = JSON.parse(decodeURIComponent(escape(atob(ctJ.content)))); }

    catData.movies = catData.movies || [];
    catData.movies.push({
      id: mediaId, tmdb_id: Number(tmdbId) || 0, title, year, poster, fanart, rating,
      original_language: origLang, genres, is_kids: isKids, tags: isKids ? ["Kids"] : [],
      source_type: sourceType,
      chunk_file: targetChunkPath,
      primary_stream_url: streamUrl,
      available_languages: ["Hindi"],
      version_count: 1
    });
    await commitGithubFile(catalogPath, catData, `Catalog (${sourceType}): ${title}`, catSha, token);

    // 3. Remove from resources/data/pending_movies.json
    pendingList.splice(index, 1);
    let pSha;
    const pRes = await fetch(`https://api.github.com/repos/${GH_REPO}/contents/resources/data/pending_movies.json?t=${Date.now()}`, { headers: { "Authorization": `token ${token}` } });
    if (pRes.ok) pSha = (await pRes.json()).sha;
    await commitGithubFile("resources/data/pending_movies.json", pendingList, `Cleared ${title} from pending`, pSha, token);

    if (!isBatch) { showStatus(`🎉 "${title}" (${sourceType}) saved to Master Catalog!`); loadPendingList(); }
  }

  async function rejectItem(index) {
    const token = getToken();
    if (!token) return alert("GitHub Token missing!");
    if (!confirm("Remove from pending_movies.json?")) return;
    pendingList.splice(index, 1);
    let pSha;
    const pRes = await fetch(`https://api.github.com/repos/${GH_REPO}/contents/resources/data/pending_movies.json?t=${Date.now()}`, { headers: { "Authorization": `token ${token}` } });
    if (pRes.ok) pSha = (await pRes.json()).sha;
    await commitGithubFile("resources/data/pending_movies.json", pendingList, "Dismissed pending item", pSha, token);
    loadPendingList();
  }

  async function commitGithubFile(path, data, msg, sha, token) {
    const res = await fetch(`https://api.github.com/repos/${GH_REPO}/contents/${path}`, {
      method: "PUT",
      headers: { "Authorization": `token ${token}`, "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg, content: btoa(unescape(encodeURIComponent(JSON.stringify(data, null, 2)))), branch: GH_BRANCH, sha })
    });
    if (!res.ok) throw new Error((await res.json()).message || "GitHub API Error");
  }

  function escapeHtml(t) { return String(t || '').replace(/[&<>"']/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m])); }
  window.addEventListener("DOMContentLoaded", loadPendingList);
</script>
</body>
</html>
