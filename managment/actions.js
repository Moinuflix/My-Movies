function transferArrivalToAddForm(index) {
  const item = inboxArrivalsList[index];
  if (!item) return;

  const addNavBtn = document.querySelectorAll('.nav-btn')[3];
  switchNav('add-items-hub', addNavBtn);
  switchHubTab('movie', document.querySelectorAll('.hub-tab-btn')[0]);

  document.getElementById('input-smart-filename').value = item.title;
  document.getElementById('input-gdrive-url').value = item.gdrive_id;
  if (item.size) {
    document.getElementById('input-filesize').value = item.size;
  }

  parseSmartFileName(item.title);
  window.scrollTo({ top: 0, behavior: 'smooth' });
  showLaserToast(`Loaded: "${item.title}" into Form`);
}

async function loadDriveArrivalsList() {
  const tbody = document.getElementById('smart-ingest-table-body');
  const statusMsg = document.getElementById('inbox-status-msg');
  if (!tbody) return;
  tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 30px;">Cross-referencing Drive files with Master data_c01.json...</td></tr>';

  try {
    const res = await fetch(`https://raw.githubusercontent.com/${GH_REPO}/${GH_BRANCH}/inbox_arrivals.json?t=${Date.now()}`);
    if (!res.ok) {
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--laser-cyan); padding: 30px;">No arrivals file found. Click "Trigger Drive Scan" first!</td></tr>';
      return;
    }

    const rawList = await res.json();
    const masterKnownIds = new Set();
    moviesData.forEach(m => {
      if (m.id) masterKnownIds.add(String(m.id).trim());
      if (m.gdrive_id) masterKnownIds.add(String(m.gdrive_id).trim());
      const match = (m.stream_url || '').match(/[?&]id=([a-zA-Z0-9_-]+)/);
      if (match) masterKnownIds.add(match[1]);
      (m.versions || []).forEach(v => {
        if (v.id) masterKnownIds.add(String(v.id).trim());
      });
    });

    inboxArrivalsList = rawList.filter(x => !masterKnownIds.has(String(x.gdrive_id).trim()));
    const count = inboxArrivalsList.length;

    const badge = document.getElementById('badge-inbox-count');
    const statInbox = document.getElementById('stat-inbox');
    if (statInbox) statInbox.textContent = count;

    if (count > 0) {
      badge.style.display = 'inline-block';
      badge.textContent = count;
      badge.classList.add('inbox-alert-badge');
      statusMsg.textContent = `🎯 Found ${count} genuine missing movies ready for addition:`;
    } else {
      badge.style.display = 'none';
      badge.classList.remove('inbox-alert-badge');
      statusMsg.textContent = '';
      tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--laser-green); font-weight: 800; font-size: 1rem; padding: 30px;">🎉 All 100% Synced! Master data_c01.json has all Google Drive movies.</td></tr>';
      return;
    }

    renderSmartScanTable(inboxArrivalsList);
  } catch (e) {
    tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--laser-red); padding: 30px;">Error: ${e.message}</td></tr>`;
  }
}

async function autoConnectFranchiseCollections() {
  const token = getStoredToken();
  if (!token) {
    showLaserToast('GitHub Token Required!', true);
    return;
  }

  showLaserToast('Connecting franchise collections...');
  let updatedCount = 0;

  moviesData.forEach(m => {
    const t = (m.title || m.name || '').toLowerCase();
    for (const [packName, pack] of Object.entries(MASTER_FRANCHISES)) {
      if (pack.alias.some(a => t.includes(a))) {
        if (m.collection !== packName) {
          m.collection = packName;
          updatedCount++;
        }
      }
    }
  });

  if (updatedCount === 0) {
    showLaserToast('All packs are already connected!');
    return;
  }

  try {
    await commitFileDirect('../chunks/data_c01.json', moviesData, `Auto-Connected ${updatedCount} Franchise Packs`, token);
    showLaserToast(`✅ Successfully connected ${updatedCount} movies into packs!`);
    filterAndRenderMovies();
  } catch(e) {
    showLaserToast(`Pack connect error: ${e.message}`, true);
  }
}

async function autoMergeDuplicateMovies() {
  const token = getStoredToken();
  if (!token) {
    showLaserToast('GitHub Token Required!', true);
    return;
  }

  showLaserToast('Scanning for duplicate movies...');
  const map = new Map();
  let mergedCount = 0;

  moviesData.forEach(m => {
    const key = m.tmdb_id ? String(m.tmdb_id) : (m.title || m.name || '').toLowerCase().trim();
    if (!map.has(key)) {
      m.versions = m.versions || [];
      map.set(key, m);
    } else {
      const existing = map.get(key);
      existing.versions = existing.versions || [];
      if (m.versions && m.versions.length > 0) {
        m.versions.forEach(v => {
          if (!existing.versions.some(ev => ev.id === v.id)) {
            existing.versions.push(v);
          }
        });
      }
      mergedCount++;
    }
  });

  if (mergedCount === 0) {
    showLaserToast('No duplicate movies found to merge!');
    return;
  }

  const deduplicated = Array.from(map.values());
  try {
    await commitFileDirect('../chunks/data_c01.json', deduplicated, `Auto-Merged ${mergedCount} Duplicate Versions`, token);
    moviesData = deduplicated;
    showLaserToast(`✅ Cleaned up and merged ${mergedCount} duplicate movies!`);
    loadAllChunks();
  } catch(e) {
    showLaserToast(`Merge error: ${e.message}`, true);
  }
}

async function commitFileDirect(chunkPath, arrayData, message, token) {
  const fullPath = chunkPath.startsWith('../') ? chunkPath.replace('../', '') : chunkPath;
  const url = `https://api.github.com/repos/${GH_REPO}/contents/${fullPath}`;
  
  const getRes = await fetch(url, { headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json' } });
  let currentSha = undefined;
  if (getRes.ok) {
    const fileInfo = await getRes.json();
    currentSha = fileInfo.sha;
  }

  const finalJson = JSON.stringify(arrayData, null, 2);
  const encoded = btoa(unescape(encodeURIComponent(finalJson)));

  const putRes = await fetch(url, {
    method: 'PUT',
    headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: message, content: encoded, branch: GH_BRANCH, sha: currentSha })
  });
  if (!putRes.ok) throw new Error(`Commit failed for ${fullPath}`);
}

async function handleMovieSubmit(e) {
  e.preventDefault();
  const tmdbId = document.getElementById('input-tmdb-id').value.trim();
  let rawGdrive = document.getElementById('input-gdrive-url').value.trim();
  const fileId = extractGDriveId(rawGdrive);

  if (!fileId) return showLaserToast('Valid Google Drive link/ID required!', true);

  if (!fetchedTmdbMetadata || String(fetchedTmdbMetadata.tmdb_id) !== tmdbId) {
    await fetchTmdbMetadata(tmdbId);
  }

  const quality = document.getElementById('input-quality').value;
  const source = document.getElementById('input-source').value;
  const codec = document.getElementById('input-codec').value;
  const audio = document.getElementById('input-audio').value;
  const channels = document.getElementById('input-channels').value;
  const languages = document.getElementById('input-languages').value;
  const fileSize = document.getElementById('input-filesize').value.trim();
  const streamUrl = `${WORKER_BASE}${fileId}${USER_AGENT}`;

  const meta = fetchedTmdbMetadata || {
    title: `Movie ${tmdbId}`, original_title: `Movie ${tmdbId}`, year: new Date().getFullYear(), tmdb_id: Number(tmdbId), rating: 7.5, plot: "", poster: "", fanart: "", trailer: "", runtime: 0, director: [], cast: [], collection: "", original_language: "en"
  };

  const multiShort = languages.includes(',') ? ' Multi' : '';
  const sizeTag = fileSize ? ` [${fileSize}]` : '';
  const versionLabel = `${quality} • ${source} • ${audio}${multiShort}${sizeTag}`;

  const versionObj = {
    id: fileId,
    name: `${meta.title} (${meta.year}) [${quality}] [${source}] [${audio}].mkv`,
    quality: versionLabel,
    source: source,
    codec: codec,
    resolution: quality,
    audio: audio,
    channels: channels,
    stream_url: streamUrl,
    specs: { resolution: quality, source: source, codec: codec, audio: audio, channels: channels, languages: languages, size: fileSize }
  };

  const lang = detectMovieLang(meta);
  let targetCategoryChunk = "../chunks/data_c01_english.json";
  if (lang === 'ta') targetCategoryChunk = "../chunks/data_c01_tamil.json";
  else if (lang === 'te') targetCategoryChunk = "../chunks/data_c01_telugu.json";
  else if (lang === 'hi') targetCategoryChunk = "../chunks/data_c01_hindi.json";

  const fullMovie = {
    id: fileId,
    name: versionObj.name,
    title: meta.title,
    original_title: meta.original_title,
    original_language: lang,
    year: meta.year,
    runtime: meta.runtime || 0,
    tmdb_id: Number(tmdbId),
    rating: meta.rating,
    collection: meta.collection || getFranchiseKey(meta) || "",
    director: meta.director || [],
    trailer: meta.trailer || "",
    cast: meta.cast || [],
    plot: meta.plot,
    poster: meta.poster,
    fanart: meta.fanart,
    stream_url: streamUrl,
    specs: versionObj.specs,
    versions: [versionObj]
  };

  openPreviewModal('../chunks/data_c01.json', fullMovie, streamUrl, fullMovie.title, moviesData, false, targetCategoryChunk);
}

function openPreviewModal(targetChunk, newEntry, streamUrl, title, activeDataArray, isUpdate = false, secondCategoryChunk = null) {
  activeStreamUrl = streamUrl;
  pendingCommit = { targetChunk, newEntry, activeDataArray, title, isUpdate, secondCategoryChunk };

  const details = document.getElementById('modal-preview-details');
  if (!details) return;
  details.innerHTML = `
    <div class="preview-item"><span class="preview-item-label">Target Chunk</span><span class="preview-item-val" style="color: var(--laser-cyan);">${targetChunk}</span></div>
    <div class="preview-item"><span class="preview-item-label">Title</span><span class="preview-item-val">${title}</span></div>
    <div><span class="preview-item-label">Stream URL</span><div class="preview-stream-text">${streamUrl}</div></div>
  `;
  document.getElementById('preview-modal').classList.add('active');
}

async function commitPendingToGitHub() {
  if (!pendingCommit) return;
  const token = getStoredToken();
  if (!token) return showLaserToast('GitHub Token required!', true);

  const btn = document.getElementById('btn-commit-github');
  btn.disabled = true;
  btn.textContent = 'Committing...';

  try {
    const { targetChunk, newEntry, title, secondCategoryChunk } = pendingCommit;
    moviesData.unshift(newEntry);
    await commitFileDirect(targetChunk, moviesData, `Studio Update: ${title}`, token);

    if (secondCategoryChunk) {
      let categoryArray = secondCategoryChunk.includes('tamil') ? tamilData :
                           (secondCategoryChunk.includes('telugu') ? teluguData :
                           (secondCategoryChunk.includes('hindi') ? hindiData : englishData));
      categoryArray.unshift(newEntry);
      await commitFileDirect(secondCategoryChunk, categoryArray, `Auto-Sync: ${newEntry.title}`, token);
    }

    showLaserToast(`Successfully committed "${title}"!`);
    closeModal();
    loadAllChunks();
  } catch (err) {
    showLaserToast(`Commit Error: ${err.message}`, true);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save & Direct Commit to GitHub';
  }
}

function closeModal() {
  const modal = document.getElementById('preview-modal');
  if (modal) modal.classList.remove('active');
  pendingCommit = null;
}

async function loadAllChunks() {
  updateTokenBadge();
  updateBackendBadge();
  const fetchChunk = async (path) => {
    try {
      const res = await fetch(`https://raw.githubusercontent.com/${GH_REPO}/${GH_BRANCH}/${path}?t=${Date.now()}`);
      if (!res.ok) return [];
      const data = await res.json();
      return Array.isArray(data) ? data : [];
    } catch(e) { return []; }
  };

  [moviesData, tamilData, teluguData, hindiData, englishData, seriesData, songsData, vaultData] = await Promise.all([
    fetchChunk('chunks/data_c01.json'),
    fetchChunk('chunks/data_c01_tamil.json'),
    fetchChunk('chunks/data_c01_telugu.json'),
    fetchChunk('chunks/data_c01_hindi.json'),
    fetchChunk('chunks/data_c01_english.json'),
    fetchChunk('chunks/data_c02.json'),
    fetchChunk('chunks/data_c03.json'),
    fetchChunk('chunks/data_c04.json')
  ]);

  document.getElementById('stat-c01').textContent = moviesData.length;
  document.getElementById('stat-tamil').textContent = tamilData.length || moviesData.filter(m => detectMovieLang(m) === 'ta').length;
  document.getElementById('stat-telugu').textContent = teluguData.length || moviesData.filter(m => detectMovieLang(m) === 'te').length;
  document.getElementById('stat-packs').textContent = Object.keys(MASTER_FRANCHISES).length;

  document.getElementById('badge-c01').textContent = moviesData.length;
  document.getElementById('badge-c02').textContent = seriesData.length;
  document.getElementById('badge-c03').textContent = songsData.length;
  document.getElementById('badge-c04').textContent = vaultData.length;

  filterAndRenderMovies();
  pollInboxNotificationBadge();
}

window.addEventListener('DOMContentLoaded', loadAllChunks);
