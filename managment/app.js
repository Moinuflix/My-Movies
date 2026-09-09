let moviesData = [];
let tamilData = [];
let teluguData = [];
let hindiData = [];
let englishData = [];

let seriesData = [];
let songsData = [];
let vaultData = [];
let inboxArrivalsList = [];

let activeUploadingCount = 0;

let isMergeMode = false;
let targetExistingMovie = null;
let fetchedTmdbMetadata = null;
let tmdbDebounceTimeout = null;
let smartSearchDebounce = null;
let pendingCommit = null;
let activeStreamUrl = '';
let currentCategoryFilter = 'packs';

let seriesDebounce = null;
let songDebounce = null;
let stageReviewList = [];

const CONFIRM_PASS = "24592";
const TMDB_API_KEY = '051ccf72e026820cb53b8b8531b6a2ba';
const GH_REPO = 'Moinuflix/My-Movies';
const GH_BRANCH = 'main';
const RAW_BASE = `https://raw.githubusercontent.com/${GH_REPO}/${GH_BRANCH}`;
const API_BASE = `https://api.github.com/repos/${GH_REPO}`;
const WORKER_BASE = 'https://gdrive-stream.moinudeentv.workers.dev/?id=';
const USER_AGENT = '|User-Agent=Kodi-MoinuTV-PrivatePlayer/1.0';

const MASTER_FRANCHISES = {
  "Pushpa Collection": {
    name: "Pushpa Collection",
    alias: ["pushpa"],
    poster: "https://image.tmdb.org/t/p/w500/1XDDpvTy1nQ9l5t9L5W09U09yR.jpg",
    allMovies: [
      { title: "Pushpa: The Rise", year: 2021, tmdb_id: 671583 },
      { title: "Pushpa 2: The Rule", year: 2024, tmdb_id: 872585 }
    ]
  },
  "K.G.F Collection": {
    name: "K.G.F Collection",
    alias: ["k.g.f", "kgf"],
    poster: "https://image.tmdb.org/t/p/w500/b1Ox59uva73r6rM2lflkgl8n8pE.jpg",
    allMovies: [
      { title: "K.G.F: Chapter 1", year: 2018, tmdb_id: 564147 },
      { title: "K.G.F: Chapter 2", year: 2022, tmdb_id: 587412 }
    ]
  },
  "Baahubali Collection": {
    name: "Baahubali Collection",
    alias: ["baahubali", "bahubali", "bāhubali"],
    poster: "https://image.tmdb.org/t/p/w500/9BAjt85amQXzhvUVvbc1sp4ZQwo.jpg",
    allMovies: [
      { title: "Bāhubali: The Beginning", year: 2015, tmdb_id: 256040 },
      { title: "Bāhubali 2: The Conclusion", year: 2017, tmdb_id: 350312 }
    ]
  },
  "The Dark Knight Collection": {
    name: "The Dark Knight Collection",
    alias: ["dark knight", "batman begins"],
    poster: "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    allMovies: [
      { title: "Batman Begins", year: 2005, tmdb_id: 272 },
      { title: "The Dark Knight", year: 2008, tmdb_id: 155 },
      { title: "The Dark Knight Rises", year: 2012, tmdb_id: 49026 }
    ]
  },
  "Spider-Man Collection": {
    name: "Spider-Man Collection",
    alias: ["spider-man", "spiderman", "no way home", "far from home", "homecoming"],
    poster: "https://image.tmdb.org/t/p/w500/1g0dhYtq4irTY1GPXvft6k4YLjm.jpg",
    allMovies: [
      { title: "Spider-Man", year: 2002, tmdb_id: 557 },
      { title: "Spider-Man: Far From Home", year: 2019, tmdb_id: 429617 },
      { title: "Spider-Man: No Way Home", year: 2021, tmdb_id: 634649 }
    ]
  },
  "Lokesh Cinematic Universe (LCU)": {
    name: "Lokesh Cinematic Universe (LCU)",
    alias: ["kaithi", "vikram", "leo", "coolie"],
    poster: "https://image.tmdb.org/t/p/w500/bL2L2gR5rE7W9M3Ww4w0eM7eW7P.jpg",
    allMovies: [
      { title: "Kaithi", year: 2019, tmdb_id: 624808 },
      { title: "Vikram", year: 2022, tmdb_id: 743563 },
      { title: "Leo", year: 2023, tmdb_id: 1072790 },
      { title: "Coolie", year: 2025, tmdb_id: 1153399 }
    ]
  }
};

function getBackendUrl() {
  return localStorage.getItem('moinuflix_backend_url') || 'http://localhost:5000/upload';
}

function configureBackendUrl() {
  const current = getBackendUrl();
  const input = prompt('Enter your Colab Ngrok/Backend URL (e.g. https://xxxx.ngrok-free.app/upload):', current);
  if (input !== null && input.trim()) {
    localStorage.setItem('moinuflix_backend_url', input.trim());
    updateBackendBadge();
    showLaserToast('Colab Backend URL Saved Successfully!');
  }
}

function updateBackendBadge() {
  const label = document.getElementById('backend-status-label');
  const url = getBackendUrl();
  if (url && !url.includes('localhost')) {
    label.textContent = '🌐 Colab API: Connected';
    label.style.color = 'var(--laser-green)';
  } else {
    label.textContent = '🌐 Colab Backend URL';
    label.style.color = 'var(--laser-cyan)';
  }
}

function updateUploadNotificationUI(delta, fileName = "") {
  activeUploadingCount += delta;
  if (activeUploadingCount < 0) activeUploadingCount = 0;

  const badge = document.getElementById('badge-upload-count');
  const dock = document.getElementById('upload-dock');
  const dockFile = document.getElementById('dock-status-file');

  if (activeUploadingCount > 0) {
    badge.style.display = 'inline-block';
    badge.textContent = activeUploadingCount;
    badge.classList.add('upload-active-badge');

    dock.style.display = 'flex';
    if (fileName) dockFile.textContent = fileName;
  } else {
    badge.textContent = '0';
    badge.style.display = 'none';
    badge.classList.remove('upload-active-badge');
    dock.style.display = 'none';
  }
}

function showLaserToast(msg, isError = false) {
  const toast = document.getElementById('laser-toast');
  toast.style.borderColor = isError ? 'var(--laser-red)' : 'var(--laser-cyan)';
  toast.innerHTML = (isError ? '❌ ' : '⚡ ') + escapeHtml(msg);
  toast.style.display = 'block';
  setTimeout(() => { toast.style.display = 'none'; }, 4500);
}

function getStoredToken() { return localStorage.getItem('moinuflix_gh_token') || ''; }
function configureGithubToken() {
  const current = getStoredToken();
  const input = prompt('Enter your GitHub Personal Access Token (ghp_...):', current);
  if (input !== null) {
    if (input.trim()) {
      localStorage.setItem('moinuflix_gh_token', input.trim());
      updateTokenBadge();
      showLaserToast('GitHub Token Saved Successfully!');
    } else {
      localStorage.removeItem('moinuflix_gh_token');
      updateTokenBadge();
    }
  }
}
function updateTokenBadge() {
  const label = document.getElementById('token-status-label');
  if (getStoredToken()) {
    label.textContent = 'Token: Active ✅';
    label.style.color = 'var(--laser-green)';
  } else {
    label.textContent = '⚙️ GitHub Token';
    label.style.color = 'var(--laser-cyan)';
  }
}

function extractGDriveId(url) {
  if (!url) return '';
  const clean = url.trim();
  const pMatch = clean.match(/[?&]id=([a-zA-Z0-9_-]+)/);
  if (pMatch && pMatch[1]) return pMatch[1];
  const fMatch = clean.match(/\/file\/d\/([a-zA-Z0-9_-]+)/);
  if (fMatch && fMatch[1]) return fMatch[1];
  const folMatch = clean.match(/\/folders\/([a-zA-Z0-9_-]+)/);
  if (folMatch && folMatch[1]) return folMatch[1];
  const rMatch = clean.match(/^[a-zA-Z0-9_-]{25,}$/);
  if (rMatch) return rMatch[0];
  return clean;
}

function escapeHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/* CLEAN PARSER: Strips Telegram prefixes (@PrakyTV - ), brackets, tags */
function cleanMovieFileName(filename) {
  let raw = filename.replace(/\.(mkv|mp4|avi|ts)$/i, '');
  raw = raw.replace(/^@[\w\-]+[\s\-_]+/i, '');
  raw = raw.replace(/[\._\-]/g, ' ');

  const ym = raw.match(/\b(19\d\d|20\d\d)\b/);
  let year = ym ? ym[1] : '';
  let title = ym ? raw.substring(0, ym.index).trim() : raw.split('[')[0].split('(')[0].trim();

  title = title.replace(/[\(\)\[\]]/g, '').trim();
  title = title.replace(/\b(1080p|720p|2160p|4k|uhd|bluray|web-dl|web|dts|atmos|ddp|x264|x265|hevc|remastered|untouched|true)\b/gi, '').trim();

  return { title: title || filename, year: year };
}

function switchNav(panelId, btn) {
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  if (btn) btn.classList.add('active');
  const targetPanel = document.getElementById(`view-${panelId}`);
  if (targetPanel) targetPanel.classList.add('active');

  if (panelId === 'drive-inbox') {
    loadDriveArrivalsList();
  } else if (panelId === 'existing-series') {
    renderSeriesGrid();
  } else if (panelId === 'existing-songs') {
    renderSongsGrid();
  } else if (panelId === 'existing-vault') {
    renderVaultGrid();
  }
}

function switchHubTab(tabType, btn) {
  document.querySelectorAll('.hub-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.hub-content').forEach(c => c.style.display = 'none');
  if (btn) btn.classList.add('active');
  const activeContent = document.getElementById(`hub-tab-${tabType}`);
  if (activeContent) activeContent.style.display = 'block';
}

function toggleLanguage(lang) {
  const input = document.getElementById('input-languages');
  let current = input.value.split(',').map(s => s.trim()).filter(Boolean);
  if (current.includes(lang)) {
    current = current.filter(l => l !== lang);
  } else {
    current.push(lang);
  }
  input.value = current.join(', ');
}

function applyMultiPreset() {
  document.getElementById('input-languages').value = "Tamil, Telugu, Hindi, Malayalam";
  showLaserToast("Multi-Audio Preset Applied: 4 Regional Tracks");
}

function detectMovieLang(movie) {
  const text = (movie.original_title || "") + " " + (movie.title || "");
  if (/[\u0B80-\u0BFF]/.test(text)) return 'ta';
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te';
  if (/[\u0900-\u097F]/.test(text)) return 'hi';
  
  const orig = String(movie.original_language || "").toLowerCase().trim();
  if (['ta', 'tam'].includes(orig)) return 'ta';
  if (['te', 'tel'].includes(orig)) return 'te';
  if (['hi', 'hin'].includes(orig)) return 'hi';
  return 'en';
}

function detectFranchiseCollection(item) {
  if (item.collection && item.collection.trim() !== '') return item.collection;
  const title = (item.title || item.name || '').toLowerCase();
  if (title.includes('pushpa')) return 'Pushpa Collection';
  if (title.includes('k.g.f') || title.includes('kgf')) return 'K.G.F Collection';
  if (title.includes('bāhubali') || title.includes('baahubali') || title.includes('bahubali')) return 'Baahubali Collection';
  if (title.includes('dark knight') || title.includes('batman begins')) return 'The Dark Knight Collection';
  if (title.includes('spider-man') || title.includes('spiderman')) return 'Spider-Man Collection';
  if (['kaithi', 'vikram', 'leo', 'coolie'].some(l => title.includes(l))) return 'Lokesh Cinematic Universe (LCU)';
  return '';
}

function getFranchiseKey(movie) {
  if (movie.collection && MASTER_FRANCHISES[movie.collection]) return movie.collection;
  const title = (movie.title || movie.name || '').toLowerCase();
  for (const [key, pack] of Object.entries(MASTER_FRANCHISES)) {
    if (pack.alias.some(a => title.includes(a))) return key;
  }
  return null;
}

async function loadAllChunks() {
  updateTokenBadge();
  updateBackendBadge();
  const fetchChunk = async (path) => {
    try {
      const res = await fetch(`${path}?t=${Date.now()}`);
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

/* RENDER SERIES (data_c02.json) */
function renderSeriesGrid() {
  const container = document.getElementById('series-grid');
  container.innerHTML = '';
  if (seriesData.length === 0) {
    container.innerHTML = '<div style="color:var(--text-muted); padding:30px;">No series found in chunks/data_c02.json.</div>';
    return;
  }
  seriesData.forEach(item => {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
      <div class="poster-wrap">
        ${item.poster ? `<img src="${item.poster}" class="poster-img" loading="lazy">` : '<div class="poster-placeholder">No Poster</div>'}
      </div>
      <div class="movie-card-body">
        <div>
          <div class="movie-title">${escapeHtml(item.name || item.title)}</div>
          <div class="movie-meta-row">
            <span class="spec-chip">${escapeHtml(item.seasons || 'Series')}</span>
          </div>
        </div>
        <button class="btn-action-primary" onclick="window.open('${escapeHtml(item.stream_url || item.gdrive || '')}', '_blank')">▶ Play Series</button>
      </div>
    `;
    container.appendChild(card);
  });
}

/* RENDER SONGS (data_c03.json) */
function renderSongsGrid() {
  const container = document.getElementById('songs-grid');
  container.innerHTML = '';
  if (songsData.length === 0) {
    container.innerHTML = '<div style="color:var(--text-muted); padding:30px;">No songs found in chunks/data_c03.json.</div>';
    return;
  }
  songsData.forEach(item => {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
      <div class="poster-wrap" style="height:210px;">
        ${item.poster ? `<img src="${item.poster}" class="poster-img" loading="lazy">` : '<div class="poster-placeholder">🎵 5.1 Track</div>'}
      </div>
      <div class="movie-card-body">
        <div>
          <div class="movie-title">${escapeHtml(item.title || item.name)}</div>
          <div class="movie-meta-row">
            <span class="spec-chip chip-ott">${escapeHtml(item.movie || 'Single')}</span>
            <span class="spec-chip chip-gold">${escapeHtml(item.quality || '5.1 Dolby')}</span>
          </div>
        </div>
        <button class="btn-action-primary" onclick="window.open('${escapeHtml(item.stream_url || item.gdrive || '')}', '_blank')">▶ Listen 5.1</button>
      </div>
    `;
    container.appendChild(card);
  });
}

/* RENDER VAULT (data_c04.json) */
function renderVaultGrid() {
  const container = document.getElementById('vault-grid');
  container.innerHTML = '';
  if (vaultData.length === 0) {
    container.innerHTML = '<div style="color:var(--text-muted); padding:30px;">No video clips found in chunks/data_c04.json.</div>';
    return;
  }
  vaultData.forEach(item => {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
      <div class="poster-wrap" style="height:200px;">
        ${item.thumbnail ? `<img src="${item.thumbnail}" class="poster-img" loading="lazy">` : '<div class="poster-placeholder">🍿 YouTube Clip</div>'}
      </div>
      <div class="movie-card-body">
        <div>
          <div class="movie-title">${escapeHtml(item.title)}</div>
          <div class="movie-meta-row">
            <span class="spec-chip">${escapeHtml(item.category || 'Clip')}</span>
          </div>
        </div>
        <button class="btn-action-primary" onclick="window.open('${escapeHtml(item.url || '')}', '_blank')">▶ Watch Video</button>
      </div>
    `;
    container.appendChild(card);
  });
}

/* CONNECT ALL PACKS */
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
    await commitFileDirect('chunks/data_c01.json', moviesData, `Auto-Connected ${updatedCount} Franchise Packs`, token);
    showLaserToast(`✅ Successfully connected ${updatedCount} movies into packs!`);
    filterAndRenderMovies();
  } catch(e) {
    showLaserToast(`Pack connect error: ${e.message}`, true);
  }
}

/* AUTO-MERGE DUPLICATES */
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
    await commitFileDirect('chunks/data_c01.json', deduplicated, `Auto-Merged ${mergedCount} Duplicate Versions`, token);
    moviesData = deduplicated;
    showLaserToast(`✅ Cleaned up and merged ${mergedCount} duplicate movies!`);
    loadAllChunks();
  } catch(e) {
    showLaserToast(`Merge error: ${e.message}`, true);
  }
}

async function pollInboxNotificationBadge() {
  try {
    const res = await fetch(`${RAW_BASE}/inbox_arrivals.json?t=${Date.now()}`);
    if (res.ok) {
      const data = await res.json();
      const existingIds = new Set(moviesData.map(m => m.id || m.gdrive_id));
      const count = Array.isArray(data) ? data.filter(x => !existingIds.has(x.gdrive_id)).length : 0;

      const badge = document.getElementById('badge-inbox-count');
      const statInbox = document.getElementById('stat-inbox');
      if (statInbox) statInbox.textContent = count;

      if (count > 0) {
        badge.style.display = 'inline-block';
        badge.textContent = count;
        badge.classList.add('inbox-alert-badge');
      } else {
        badge.style.display = 'none';
        badge.classList.remove('inbox-alert-badge');
      }
    }
  } catch (e) {}
}

async function triggerGitHubScanAction() {
  const token = getStoredToken();
  if (!token) {
    showLaserToast('GitHub Token required! Click ⚙️ GitHub Token in sidebar.', true);
    return;
  }

  const btn = document.getElementById('btn-trigger-action');
  const statusMsg = document.getElementById('inbox-status-msg');
  btn.disabled = true;
  btn.textContent = '⏳ Triggering GitHub Action...';
  statusMsg.textContent = 'Contacting GitHub API to dispatch scan_drive.yml...';

  try {
    const res = await fetch(`${API_BASE}/actions/workflows/scan_drive.yml/dispatches`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ ref: GH_BRANCH })
    });

    if (res.status === 204 || res.ok) {
      showLaserToast('🚀 Scan workflow started! Scanning Google Drive in background...');
      statusMsg.textContent = 'Background scan running on GitHub (~25-30s)... Auto-refreshing soon!';
      setTimeout(() => {
        loadDriveArrivalsList();
        btn.disabled = false;
        btn.textContent = '⚡ Trigger Drive Scan (GitHub Action)';
      }, 28000);
    } else {
      const err = await res.json();
      throw new Error(err.message || 'Dispatch failed');
    }
  } catch (e) {
    showLaserToast(`Trigger Failed: ${e.message}`, true);
    statusMsg.textContent = `Trigger Error: ${e.message}`;
    btn.disabled = false;
    btn.textContent = '⚡ Trigger Drive Scan (GitHub Action)';
  }
}

async function loadDriveArrivalsList() {
  const tbody = document.getElementById('smart-ingest-table-body');
  const statusMsg = document.getElementById('inbox-status-msg');
  tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 30px;">Cross-referencing Drive files with Master data_c01.json...</td></tr>';

  try {
    const res = await fetch(`${RAW_BASE}/inbox_arrivals.json?t=${Date.now()}`);
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

/* DIRECT AUTO-TRANSFER FROM DRIVE ARRIVALS TO ADD ITEMS FORM */
function transferArrivalToAddForm(index) {
  const item = inboxArrivalsList[index];
  if (!item) return;

  // 1. Open "➕ Add Items" Tab
  const addNavBtn = document.querySelectorAll('.nav-btn')[3];
  switchNav('add-items-hub', addNavBtn);
  switchHubTab('movie', document.querySelectorAll('.hub-tab-btn')[0]);

  // 2. Transfer Real File Name, Drive ID & Size
  document.getElementById('input-smart-filename').value = item.title;
  document.getElementById('input-gdrive-url').value = item.gdrive_id;
  if (item.size) {
    document.getElementById('input-filesize').value = item.size;
  }

  // 3. Trigger Form Auto-parse & TMDB Suggestions Dropdown
  parseSmartFileName(item.title);

  window.scrollTo({ top: 0, behavior: 'smooth' });
  showLaserToast(`Loaded: "${item.title}" into Form`);
}

function renderSmartScanTable(items) {
  const tbody = document.getElementById('smart-ingest-table-body');
  tbody.innerHTML = '';

  items.forEach((item, index) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>
        <span style="font-family: monospace; font-size: 0.78rem; color: var(--laser-cyan); font-weight: 700;">
          ${escapeHtml(item.gdrive_id.substring(0, 14))}...
        </span>
      </td>
      <td>
        <div style="font-size: 0.85rem; color: #fff; font-weight: 600; line-height: 1.4; word-break: break-all;">
          ${escapeHtml(item.title)}
        </div>
      </td>
      <td>
        <span class="clean-gb-badge">${escapeHtml(item.size || '10 GB')}</span>
      </td>
      <td style="text-align: right;">
        <button type="button" class="btn-action-primary" style="padding: 8px 14px; font-weight: 800; font-size: 0.82rem;" onclick="transferArrivalToAddForm(${index})">
          ⚡ Load in Add Form ➔
        </button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function setCategoryFilter(cat, btn) {
  currentCategoryFilter = cat;
  document.querySelectorAll('.cat-pill').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filterAndRenderMovies();
}

function filterAndRenderMovies() {
  const container = document.getElementById('movies-grid-container');
  container.innerHTML = '';
  const query = document.getElementById('movie-search-input').value.toLowerCase().trim();

  if (currentCategoryFilter === 'packs') {
    Object.entries(MASTER_FRANCHISES).forEach(([franchiseKey, packInfo]) => {
      const ownedMovies = moviesData.filter(m => getFranchiseKey(m) === franchiseKey);
      const totalExpected = packInfo.allMovies.length;
      const ownedCount = ownedMovies.length;
      const missingCount = Math.max(0, totalExpected - ownedCount);
      const isComplete = ownedCount >= totalExpected;

      if (query && !franchiseKey.toLowerCase().includes(query)) {
        const hasMatch = ownedMovies.some(m => (m.title||'').toLowerCase().includes(query));
        if (!hasMatch) return;
      }

      const poster = (ownedMovies[0] && ownedMovies[0].poster) ? ownedMovies[0].poster : packInfo.poster;

      const card = document.createElement('div');
      card.className = 'movie-card pack-card';
      card.innerHTML = `
        <div class="poster-wrap">
          <div class="universe-badge">👑 FRANCHISE PACK</div>
          <div class="pack-status-badge ${isComplete ? 'badge-complete' : 'badge-missing'}">
            ${isComplete ? `🟢 ${ownedCount}/${totalExpected} COMPLETE` : `⚠️ ${ownedCount} / ${totalExpected} (${missingCount} MISSING)`}
          </div>
          <img src="${poster}" class="poster-img" loading="lazy">
        </div>
        <div class="movie-card-body">
          <div>
            <div class="movie-title">${escapeHtml(packInfo.name)}</div>
            <div class="movie-meta-row">
              <span>${ownedCount} Movies Collected</span>
              <span>•</span>
              <span style="color:${isComplete ? 'var(--laser-green)' : 'var(--gold-lcu)'}; font-weight:800;">
                ${isComplete ? '100% Collected' : `${missingCount} Pending`}
              </span>
            </div>
          </div>
          <button type="button" class="btn-action-primary" style="margin-top:0.5rem;" onclick="openPackModal('${franchiseKey}')">
            🔍 OPEN PACK & CHECKLIST
          </button>
        </div>
      `;
      container.appendChild(card);
    });
  } else {
    moviesData.forEach((movie, index) => {
      if (query && !(movie.title||'').toLowerCase().includes(query) && !(movie.original_title||'').toLowerCase().includes(query)) return;

      const lang = detectMovieLang(movie);
      if (currentCategoryFilter === 'lang_ta' && lang !== 'ta') return;
      if (currentCategoryFilter === 'lang_te' && lang !== 'te') return;
      if (currentCategoryFilter === 'lang_hi' && lang !== 'hi') return;
      if (currentCategoryFilter === 'lang_en' && lang !== 'en') return;

      const plotText = (movie.plot || "").toLowerCase();
      if (currentCategoryFilter === 'genre_horror' && !plotText.includes('horror') && !plotText.includes('ghost')) return;
      if (currentCategoryFilter === 'genre_crime' && !plotText.includes('crime') && !plotText.includes('murder') && !plotText.includes('investigation')) return;
      if (currentCategoryFilter === 'genre_action' && !plotText.includes('action') && !plotText.includes('fight') && !plotText.includes('gangster')) return;
      if (currentCategoryFilter === 'genre_comedy' && !plotText.includes('comedy') && !plotText.includes('funny') && !plotText.includes('humor')) return;
      if (currentCategoryFilter === 'genre_romance' && !plotText.includes('romance') && !plotText.includes('love')) return;

      const isMulti = (movie.specs?.languages && movie.specs.languages.includes(',')) || (movie.name && movie.name.toLowerCase().includes('multi'));
      let sourceName = movie.specs?.source || "WEB-DL";

      const card = document.createElement('div');
      card.className = 'movie-card';
      card.innerHTML = `
        <div class="poster-wrap">
          ${movie.collection ? `<div class="universe-badge">👑 ${escapeHtml(movie.collection)}</div>` : ''}
          ${isMulti ? `<div class="multi-badge">⚡ MULTI AUDIO</div>` : ''}
          ${movie.poster ? `<img src="${movie.poster}" class="poster-img" loading="lazy">` : '<div class="poster-placeholder">No Poster</div>'}
        </div>
        <div class="movie-card-body">
          <div>
            <div class="movie-title">${escapeHtml(movie.title)}</div>
            <div class="movie-meta-row">
              <span>${escapeHtml(movie.year || 'N/A')}</span>
              <span>•</span>
              <span class="spec-chip chip-ott">${escapeHtml(sourceName)}</span>
              <span class="spec-chip">${escapeHtml(movie.specs?.resolution || '1080p')}</span>
              ${movie.specs?.size ? `<span class="clean-gb-badge">${escapeHtml(movie.specs.size)}</span>` : ''}
              ${movie.specs?.audio ? `<span class="spec-chip chip-gold">${escapeHtml(movie.specs.audio)}</span>` : ''}
            </div>
            ${movie.specs?.languages ? `<div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:8px;">🌐 ${escapeHtml(movie.specs.languages)}</div>` : ''}
          </div>
          <div class="card-actions-row">
            <button type="button" class="btn-action-primary" onclick="prepareAddVersion('${movie.tmdb_id}')">+ VERSION</button>
            <button type="button" class="btn-delete-item" onclick="promptDeleteItem('chunks/data_c01.json', ${index}, '${escapeHtml(movie.title)}', moviesData)">🗑️</button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });
  }
}

/* DELETE FUNCTION - WITH CONFIRM PIN & DUAL SYNC */
async function promptDeleteItem(chunkPath, index, itemTitle, dataArray) {
  const pass = prompt(`Delete "${itemTitle}"?\nEnter confirmation PIN:`);
  if (pass !== CONFIRM_PASS) {
    if (pass !== null) showLaserToast('Incorrect PIN! Deletion aborted.', true);
    return;
  }

  const token = getStoredToken();
  if (!token) {
    showLaserToast('GitHub Token missing! Click ⚙️ GitHub Token in sidebar.', true);
    return;
  }

  showLaserToast(`Deleting "${itemTitle}"...`);

  const deletedItem = dataArray[index];
  dataArray.splice(index, 1);

  try {
    await commitFileDirect(chunkPath, dataArray, `Studio Delete: Removed ${itemTitle} from ${chunkPath}`, token);

    if (deletedItem && deletedItem.tmdb_id) {
      const lang = detectMovieLang(deletedItem);
      let catChunk = "chunks/data_c01_english.json";
      let catArray = englishData;
      if (lang === 'ta') { catChunk = "chunks/data_c01_tamil.json"; catArray = tamilData; }
      else if (lang === 'te') { catChunk = "chunks/data_c01_telugu.json"; catArray = teluguData; }
      else if (lang === 'hi') { catChunk = "chunks/data_c01_hindi.json"; catArray = hindiData; }

      const catIdx = catArray.findIndex(m => String(m.tmdb_id) === String(deletedItem.tmdb_id));
      if (catIdx >= 0) {
        catArray.splice(catIdx, 1);
        await commitFileDirect(catChunk, catArray, `Studio Delete Sync: Removed ${itemTitle}`, token);
      }
    }

    showLaserToast(`"${itemTitle}" successfully deleted!`);
    loadAllChunks();
  } catch (err) {
    showLaserToast(`Delete Failed: ${err.message}`, true);
    loadAllChunks();
  }
}

function openPackModal(franchiseKey) {
  const packInfo = MASTER_FRANCHISES[franchiseKey];
  if (!packInfo) return;

  const ownedMovies = moviesData.filter(m => getFranchiseKey(m) === franchiseKey);
  document.getElementById('pack-modal-title').textContent = packInfo.name;
  document.getElementById('pack-modal-subtitle').textContent = `Total: ${packInfo.allMovies.length} | Owned: ${ownedMovies.length}`;
  document.getElementById('pack-owned-count').textContent = ownedMovies.length;

  const ownedList = document.getElementById('pack-owned-list');
  ownedList.innerHTML = '';
  ownedMovies.forEach(m => {
    const item = document.createElement('div');
    item.className = 'pack-movie-item';
    item.innerHTML = `
      <div>
        <div style="font-weight:700; color:#fff;">${escapeHtml(m.title)} (${m.year || 'N/A'})</div>
        <div style="font-size:0.75rem; color:var(--laser-green);">Ready • ${m.specs?.languages || 'Standard'}</div>
      </div>
      <button class="btn-action-primary" style="flex:none; padding:0.4rem 0.9rem;" onclick="copyStream('${escapeHtml(m.stream_url||'')}')">📋 Stream</button>
    `;
    ownedList.appendChild(item);
  });

  const missingMovies = packInfo.allMovies.filter(expected => {
    return !ownedMovies.some(owned => (owned.title || '').toLowerCase().includes(expected.title.toLowerCase()) || (owned.tmdb_id && Number(owned.tmdb_id) === Number(expected.tmdb_id)));
  });

  document.getElementById('pack-missing-count').textContent = missingMovies.length;
  const missingList = document.getElementById('pack-missing-list');
  missingList.innerHTML = '';
  if (missingMovies.length === 0) {
    document.getElementById('pack-missing-section').style.display = 'none';
  } else {
    document.getElementById('pack-missing-section').style.display = 'block';
    missingMovies.forEach(m => {
      const item = document.createElement('div');
      item.className = 'pack-movie-item item-missing';
      item.innerHTML = `
        <div>
          <div style="font-weight:700; color:#f87171;">${escapeHtml(m.title)} (${m.year})</div>
          <div style="font-size:0.75rem; color:var(--text-dim);">TMDB ID: ${m.tmdb_id} • Missing from Library</div>
        </div>
        <span style="font-size:0.75rem; color:#f87171; font-weight:800;">Not In Drive</span>
      `;
      missingList.appendChild(item);
    });
  }
  document.getElementById('pack-modal').classList.add('active');
}
function closePackModal() { document.getElementById('pack-modal').classList.remove('active'); }

function parseSpecsFromFileName(filename) {
  const fn = filename.toLowerCase();
  let res = "1080p FHD", quality = "1080p", source = "WEB-DL", codec = "x265", audio = "Dolby Atmos", channels = "5.1", langs = [];

  if (fn.includes('2160p') || fn.includes('4k') || fn.includes('uhd')) { res = "4K UHD"; quality = "4K UHD"; }
  else if (fn.includes('720p')) { res = "720p HD"; quality = "720p"; }

  if (fn.includes('nf') || fn.includes('netflix')) source = "Netflix";
  else if (fn.includes('dsnp') || fn.includes('hotstar') || fn.includes('disney')) source = "Disney+ Hotstar";
  else if (fn.includes('sony') || fn.includes('sonyliv')) source = "SonyLIV";
  else if (fn.includes('amzn') || fn.includes('prime')) source = "Prime Video";
  else if (fn.includes('zee5')) source = "Zee5";
  else if (fn.includes('jio')) source = "JioCinema";
  else if (fn.includes('aha')) source = "Aha Video";
  else if (fn.includes('bluray') || fn.includes('remux')) source = "BLURAY";

  if (fn.includes('multi') || fn.includes('dual')) {
    langs = ["Tamil", "Telugu", "Hindi", "Malayalam"];
  } else {
    const langMap = { "tamil": "Tamil", "tam": "Tamil", "telugu": "Telugu", "tel": "Telugu", "hindi": "Hindi", "hin": "Hindi", "malayalam": "Malayalam", "mal": "Malayalam", "kannada": "Kannada", "english": "English" };
    for (let [k, v] of Object.entries(langMap)) {
      let pattern = new RegExp("(^|[._\\-\\[\\(])" + k + "([._\\-\\]\\)]|$)", "i");
      if (pattern.test(fn)) { if (!langs.includes(v)) langs.push(v); }
    }
  }

  return {
    resolution: res,
    quality: quality,
    source: source,
    codec: fn.includes('x264') || fn.includes('h264') ? "H.264" : "x265",
    audio: fn.includes('ddp') ? "Dolby Digital Plus" : (fn.includes('ac3') ? "Dolby Digital" : "Dolby Atmos"),
    channels: fn.includes('7.1') ? "7.1" : "5.1",
    languages: langs.length > 0 ? langs.join(', ') : "Tamil"
  };
}

function parseSmartFileName(filename) {
  if (!filename || filename.trim().length === 0) {
    document.getElementById('parsed-smart-tags').innerHTML = '';
    document.getElementById('tmdb-suggestions-box').style.display = 'none';
    return;
  }
  const specs = parseSpecsFromFileName(filename);
  document.getElementById('input-quality').value = specs.quality;
  document.getElementById('input-source').value = specs.source;
  document.getElementById('input-codec').value = specs.codec;
  document.getElementById('input-audio').value = specs.audio;
  document.getElementById('input-channels').value = specs.channels;
  document.getElementById('input-languages').value = specs.languages;

  const tags = [specs.source, specs.quality, specs.codec, specs.audio, specs.languages];
  document.getElementById('parsed-smart-tags').innerHTML = tags.map(t => `<span class="smart-tag">✔ ${t}</span>`).join(' ');

  clearTimeout(smartSearchDebounce);
  smartSearchDebounce = setTimeout(() => { searchMovieFromFilename(filename); }, 350);
}

async function searchMovieFromFilename(rawName) {
  const parsed = cleanMovieFileName(rawName);
  let movieTitle = parsed.title;
  let year = parsed.year;

  if (!movieTitle || movieTitle.length < 2) return;

  try {
    const res = await fetch(`https://api.themoviedb.org/3/search/movie?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(movieTitle)}${year ? `&year=${year}` : ''}&language=en-US`);
    const data = await res.json();
    const results = data.results || [];
    const box = document.getElementById('tmdb-suggestions-box');
    const list = document.getElementById('tmdb-suggestions-list');
    list.innerHTML = '';

    if (results.length > 0) {
      results.slice(0, 6).forEach(m => {
        const y = m.release_date ? m.release_date.split('-')[0] : 'N/A';
        const poster = m.poster_path ? `https://image.tmdb.org/t/p/w92${m.poster_path}` : '';
        const item = document.createElement('div');
        item.className = 'tmdb-result-item';
        item.innerHTML = `
          ${poster ? `<img src="${poster}" class="tmdb-result-poster">` : '<div class="tmdb-result-poster"></div>'}
          <div class="tmdb-result-info">
            <div class="tmdb-result-title">${escapeHtml(m.title)} (${y})</div>
            <div class="tmdb-result-meta">TMDB ID: <b>${m.id}</b> • ★ ${m.vote_average ? m.vote_average.toFixed(1) : 'N/A'}</div>
          </div>
        `;
        item.onclick = () => {
          document.getElementById('input-tmdb-id').value = m.id;
          checkTmdbMatch();
          box.style.display = 'none';
          showLaserToast(`Selected: "${m.title}" (${y})`);
        };
        list.appendChild(item);
      });
      box.style.display = 'block';
    } else { box.style.display = 'none'; }
  } catch(e) { document.getElementById('tmdb-suggestions-box').style.display = 'none'; }
}

async function fetchTmdbMetadata(tmdbId) {
  if (!tmdbId || parseInt(tmdbId) <= 0) return null;
  try {
    const res = await fetch(`https://api.themoviedb.org/3/movie/${tmdbId}?api_key=${TMDB_API_KEY}&language=en-US&append_to_response=videos,credits`);
    if (!res.ok) return null;
    const data = await res.json();

    let trailerUrl = "";
    if (data.videos && data.videos.results) {
      let t = data.videos.results.find(v => v.type === "Trailer" && v.site === "YouTube");
      if (t) trailerUrl = `https://www.youtube.com/watch?v=${t.key}`;
    }

    const directors = (data.credits && data.credits.crew) ? data.credits.crew.filter(c => c.job === "Director").map(c => c.name) : [];
    const castList = [];
    if (data.credits && data.credits.cast) {
      data.credits.cast.slice(0, 5).forEach(c => {
        castList.push({ name: c.name, role: c.character || "", thumbnail: c.profile_path ? `https://image.tmdb.org/t/p/w185${c.profile_path}` : "" });
      });
    }

    fetchedTmdbMetadata = {
      title: data.title || `Movie ${tmdbId}`,
      original_title: data.original_title || data.title,
      original_language: data.original_language || 'en',
      year: data.release_date ? parseInt(data.release_date.split('-')[0]) : new Date().getFullYear(),
      tmdb_id: data.id,
      rating: data.vote_average ? Number(data.vote_average.toFixed(1)) : 7.5,
      runtime: data.runtime || 0,
      director: directors,
      cast: castList,
      collection: (data.belongs_to_collection && data.belongs_to_collection.name) ? data.belongs_to_collection.name : detectFranchiseCollection(data),
      plot: data.overview || '',
      poster: data.poster_path ? `https://image.tmdb.org/t/p/w500${data.poster_path}` : '',
      fanart: data.backdrop_path ? `https://image.tmdb.org/t/p/original${data.backdrop_path}` : '',
      trailer: trailerUrl
    };
    return fetchedTmdbMetadata;
  } catch (e) { return null; }
}

function checkTmdbMatch() {
  const enteredId = document.getElementById('input-tmdb-id').value.trim();
  const hint = document.getElementById('tmdb-match-hint');
  clearTimeout(tmdbDebounceTimeout);

  if (!enteredId) {
    hint.textContent = 'Auto-fetches Official Title, Poster, Cast, Director, Trailer & Industry';
    hint.style.color = 'var(--text-dim)';
    return;
  }

  tmdbDebounceTimeout = setTimeout(async () => {
    const meta = await fetchTmdbMetadata(enteredId);
    if (meta) {
      hint.textContent = `Found: "${meta.title}" (${meta.year}) • Lang: ${meta.original_language.toUpperCase()}`;
      hint.style.color = 'var(--laser-green)';
    }
  }, 400);
}

function prepareAddVersion(tmdbId) {
  const existing = moviesData.find(m => String(m.tmdb_id) === String(tmdbId));
  if (!existing) return;
  isMergeMode = true;
  targetExistingMovie = existing;

  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('view-add-items-hub').classList.add('active');
  switchHubTab('movie', document.querySelectorAll('.hub-tab-btn')[0]);

  document.getElementById('input-tmdb-id').value = existing.tmdb_id;
  document.getElementById('btn-movie-submit').textContent = 'ONE-CLICK MERGE';
  document.getElementById('btn-cancel-merge').style.display = 'inline-block';
}

function cancelMergeMode() {
  isMergeMode = false;
  targetExistingMovie = null;
  document.getElementById('btn-movie-submit').textContent = 'ADD MOVIE';
  document.getElementById('btn-cancel-merge').style.display = 'none';
}

async function handleMovieSubmit(e) {
  e.preventDefault();
  const tmdbId = document.getElementById('input-tmdb-id').value.trim();
  let rawGdrive = document.getElementById('input-gdrive-url').value.trim();
  const directUrl = document.getElementById('input-direct-download-url').value.trim();

  const submitBtn = document.getElementById('btn-movie-submit');

  if (!rawGdrive && directUrl) {
    const movieFileName = document.getElementById('input-smart-filename').value.trim() || `Movie_${tmdbId}.mkv`;
    
    updateUploadNotificationUI(1, movieFileName);
    showLaserToast("Downloading to Google Drive in progress... Please wait!");
    submitBtn.disabled = true;
    submitBtn.textContent = '⏳ DOWNLOADING TO GDRIVE...';

    try {
      const backendEndpoint = getBackendUrl();
      const resp = await fetch(backendEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: directUrl,
          filename: movieFileName
        })
      });

      if (!resp.ok) {
        throw new Error(`Server returned error: ${resp.status}`);
      }

      const resData = await resp.json();
      if (resData && resData.gdrive_id) {
        rawGdrive = resData.gdrive_id;
        document.getElementById('input-gdrive-url').value = rawGdrive;
        showLaserToast("✅ Google Drive Upload Complete!");
      } else {
        throw new Error("Server completed download but no Google Drive ID was returned.");
      }
    } catch(err) {
      showLaserToast(`Upload Failed: ${err.message}`, true);
      updateUploadNotificationUI(-1);
      submitBtn.disabled = false;
      submitBtn.textContent = isMergeMode ? 'ONE-CLICK MERGE' : 'ADD MOVIE';
      return;
    } finally {
      updateUploadNotificationUI(-1);
      submitBtn.disabled = false;
      submitBtn.textContent = isMergeMode ? 'ONE-CLICK MERGE' : 'ADD MOVIE';
    }
  }

  const fileId = extractGDriveId(rawGdrive);
  if (!fileId || fileId.startsWith('DRIVE_AUTO_')) {
    return showLaserToast('Valid Google Drive link/ID required!', true);
  }

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
  let targetCategoryChunk = "chunks/data_c01_english.json";
  if (lang === 'ta') targetCategoryChunk = "chunks/data_c01_tamil.json";
  else if (lang === 'te') targetCategoryChunk = "chunks/data_c01_telugu.json";
  else if (lang === 'hi') targetCategoryChunk = "chunks/data_c01_hindi.json";

  if (isMergeMode && targetExistingMovie) {
    targetExistingMovie.versions = targetExistingMovie.versions || [];
    targetExistingMovie.versions.push(versionObj);
    openPreviewModal('chunks/data_c01.json', targetExistingMovie, streamUrl, `${targetExistingMovie.title} (Added ${quality})`, moviesData, true, targetCategoryChunk);
  } else {
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
      collection: meta.collection || detectFranchiseCollection(meta),
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
    openPreviewModal('chunks/data_c01.json', fullMovie, streamUrl, fullMovie.title, moviesData, false, targetCategoryChunk);
  }
}

function openPreviewModal(targetChunk, newEntry, streamUrl, title, activeDataArray, isUpdate = false, secondCategoryChunk = null) {
  activeStreamUrl = streamUrl;
  pendingCommit = { targetChunk, newEntry, activeDataArray, title, isUpdate, secondCategoryChunk };

  const details = document.getElementById('modal-preview-details');
  details.innerHTML = `
    <div class="preview-item"><span class="preview-item-label">Target Chunk</span><span class="preview-item-val" style="color: var(--laser-cyan);">${targetChunk} ${secondCategoryChunk ? `+ ${secondCategoryChunk}` : ''}</span></div>
    <div class="preview-item"><span class="preview-item-label">Title / Action</span><span class="preview-item-val">${title}</span></div>
    <div><span class="preview-item-label">Stream / Info</span><div class="preview-stream-text">${streamUrl}</div></div>
  `;
  document.getElementById('preview-modal').classList.add('active');
}

async function commitPendingToGitHub() {
  if (!pendingCommit) return;
  const token = getStoredToken();
  if (!token) return showLaserToast('GitHub Token required! Click ⚙️ GitHub Token.', true);

  const btn = document.getElementById('btn-commit-github');
  btn.disabled = true;
  btn.textContent = 'Committing...';

  try {
    const { targetChunk, newEntry, activeDataArray, title, isUpdate, secondCategoryChunk } = pendingCommit;
    if (newEntry && !isUpdate) activeDataArray.unshift(newEntry);

    await commitFileDirect(targetChunk, activeDataArray, `Studio Update: ${title} in ${targetChunk}`, token);

    if (secondCategoryChunk && newEntry) {
      let categoryArray = [];
      if (secondCategoryChunk.includes('tamil')) categoryArray = tamilData;
      else if (secondCategoryChunk.includes('telugu')) categoryArray = teluguData;
      else if (secondCategoryChunk.includes('hindi')) categoryArray = hindiData;
      else if (secondCategoryChunk.includes('english')) categoryArray = englishData;

      const existingIdx = categoryArray.findIndex(m => String(m.tmdb_id) === String(newEntry.tmdb_id));
      if (existingIdx >= 0) categoryArray[existingIdx] = newEntry;
      else categoryArray.unshift(newEntry);

      await commitFileDirect(secondCategoryChunk, categoryArray, `Auto-Sync Category: ${newEntry.title}`, token);
    }

    try {
      const inboxFileRes = await fetch(`${API_BASE}/contents/inbox_arrivals.json`, {
        headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github.v3+json' }
      });
      if (inboxFileRes.ok) {
        const inboxData = await inboxFileRes.json();
        const currentList = JSON.parse(decodeURIComponent(escape(atob(inboxData.content.replace(/\n/g, '')))));
        const filtered = currentList.filter(x => x.gdrive_id !== newEntry.id);
        if (filtered.length !== currentList.length) {
          await commitFileDirect('inbox_arrivals.json', filtered, `Clear ${newEntry.title} from inbox`, token);
        }
      }
    } catch(e) {}

    showLaserToast(`Successfully committed "${title}"!`);
    closeModal();
    cancelMergeMode();
    loadAllChunks();
  } catch (err) {
    showLaserToast(`Commit Error: ${err.message}`, true);
  } finally {
    btn.disabled = false;
    btn.textContent = 'Save & Direct Commit to GitHub';
  }
}

async function commitFileDirect(chunkPath, arrayData, message, token) {
  const url = `https://api.github.com/repos/${GH_REPO}/contents/${chunkPath}`;
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
  if (!putRes.ok) throw new Error(`Commit failed for ${chunkPath}`);
}

function closeModal() {
  document.getElementById('preview-modal').classList.remove('active');
  pendingCommit = null;
}

async function copyStreamUrl() {
  if (!activeStreamUrl) return;
  await navigator.clipboard.writeText(activeStreamUrl);
  showLaserToast('Stream URL copied!');
}

async function copyStream(url) {
  if (!url) return showLaserToast('No stream URL attached', true);
  await navigator.clipboard.writeText(url);
  showLaserToast('Stream link copied!');
}

function handleMovieSearch() { filterAndRenderMovies(); }

window.addEventListener('DOMContentLoaded', loadAllChunks);