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
let currentTmdbPickIndex = null;

const CONFIRM_PASS = "24592";
const TMDB_API_KEY = '051ccf72e026820cb53b8b8531b6a2ba';
const GH_REPO = 'Moinuflix/My-Movies';
const GH_BRANCH = 'main';
const RAW_BASE = `https://raw.githubusercontent.com/${GH_REPO}/${GH_BRANCH}`;
const API_BASE = `https://api.github.com/repos/${GH_REPO}`;
const WORKER_BASE = 'https://gdrive-stream.moinudeentv.workers.dev/?id=';
const USER_AGENT = '|User-Agent=Kodi-MoinuTV-PrivatePlayer/1.0';

/* BASE POPULAR FRANCHISES + DYNAMIC REGISTRY */
const MASTER_FRANCHISES = {
  "Demonte Colony Collection": {
    name: "Demonte Colony Collection",
    alias: ["demonte colony"],
    poster: "https://image.tmdb.org/t/p/w500/lZmH9hea8fstTK49fplSQS0NWUd.jpg",
    allMovies: [
      { title: "Demonte Colony", year: 2015, tmdb_id: 342502 },
      { title: "Demonte Colony 2", year: 2024, tmdb_id: 979250 },
      { title: "Demonte Colony 3 (Coming Soon)", year: 2026, tmdb_id: 0 }
    ]
  },
  "HIT Verse": {
    name: "HIT Verse",
    alias: ["hit: the", "hard hit"],
    poster: "https://image.tmdb.org/t/p/w500/wT9tGyFol4RBwkjESXUWeBdnLJn.jpg",
    allMovies: [
      { title: "HIT: The First Case", year: 2020, tmdb_id: 678391 },
      { title: "HIT: The 2nd Case", year: 2022, tmdb_id: 811945 },
      { title: "HIT: The Third Case", year: 2025, tmdb_id: 1060046 }
    ]
  },
  "Dhilluku Dhuddu Collection": {
    name: "Dhilluku Dhuddu Collection",
    alias: ["dhilluku dhuddu", "dd returns"],
    poster: "https://image.tmdb.org/t/p/w500/aautnOfweBUF74nmwRI2iSf8VdL.jpg",
    allMovies: [
      { title: "Dhilluku Dhuddu", year: 2016, tmdb_id: 404711 },
      { title: "Dhilluku Dhuddu 2", year: 2019, tmdb_id: 579417 },
      { title: "DD Returns", year: 2023, tmdb_id: 1153886 }
    ]
  },
  "Singam Collection": {
    name: "Singam Collection",
    alias: ["singam", "si 3"],
    poster: "https://image.tmdb.org/t/p/w500/6ENAxfZz4IY2NPu89R1SGObjiWF.jpg",
    allMovies: [
      { title: "Singam", year: 2010, tmdb_id: 40166 },
      { title: "Singam 2", year: 2013, tmdb_id: 191735 },
      { title: "Si 3", year: 2017, tmdb_id: 376440 }
    ]
  },
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
      { title: "K.G.F: Chapter 2", year: 2022, tmdb_id: 587412 },
      { title: "K.G.F: Chapter 3 (Coming Soon)", year: 2027, tmdb_id: 0 }
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

function showLaserToast(msg, isError = false) {
  const toast = document.getElementById('laser-toast');
  if (!toast) return;
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
  if (!label) return;
  if (getStoredToken()) {
    label.textContent = 'Token: Active ✅';
    label.style.color = 'var(--laser-green)';
  } else {
    label.textContent = '⚙️ GitHub Token';
    label.style.color = 'var(--laser-cyan)';
  }
}

function getBackendUrl() { return localStorage.getItem('moinuflix_backend_url') || ''; }
function configureBackendUrl() {
  const current = getBackendUrl();
  const input = prompt('Enter your Colab Backend URL:', current);
  if (input !== null && input.trim()) {
    localStorage.setItem('moinuflix_backend_url', input.trim());
    updateBackendBadge();
    showLaserToast('Backend URL Saved!');
  }
}
function updateBackendBadge() {
  const label = document.getElementById('backend-status-label');
  if (!label) return;
  const url = getBackendUrl();
  if (url && !url.includes('localhost')) {
    label.textContent = '🌐 Colab: Connected';
    label.style.color = 'var(--laser-green)';
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

/* SMART DYNAMIC FRANCHISE & SEQUEL DETECTOR */
function getFranchiseKey(movie) {
  // 1. Check direct hardcoded collection match
  if (movie.collection && MASTER_FRANCHISES[movie.collection]) {
    return movie.collection;
  }

  // 2. Check title against existing collection aliases
  const rawTitle = (movie.title || movie.name || '').toLowerCase();
  for (const [key, pack] of Object.entries(MASTER_FRANCHISES)) {
    if (pack.alias.some(a => rawTitle.includes(a))) {
      return key;
    }
  }

  // 3. Dynamic Collection Creation from TMDB "collection" key
  if (movie.collection && movie.collection.trim() !== '') {
    const colName = movie.collection.trim();
    if (!MASTER_FRANCHISES[colName]) {
      MASTER_FRANCHISES[colName] = {
        name: colName,
        alias: [colName.toLowerCase().replace(/collection|verse/gi, '').trim()],
        poster: movie.poster || '',
        allMovies: [
          { title: movie.title, year: movie.year || 2024, tmdb_id: movie.tmdb_id || 0 }
        ]
      };
    }
    return colName;
  }

  // 4. Auto-detect Sequels / Parts (e.g. "Demonte Colony 2", "Gatta Kusthi 2")
  const sequelMatch = movie.title ? movie.title.match(/^(.*?)(?:\s*(?:Part|Chapter|Volume)?\s*([2-9]))$/i) : null;
  if (sequelMatch) {
    const baseName = sequelMatch[1].trim();
    const currentPartNum = parseInt(sequelMatch[2], 10);
    const generatedPackName = `${baseName} Collection`;

    if (!MASTER_FRANCHISES[generatedPackName]) {
      const generatedList = [];
      for (let i = 1; i <= currentPartNum; i++) {
        generatedList.push({
          title: i === 1 ? baseName : `${baseName} ${i}`,
          year: i === currentPartNum ? (movie.year || 2024) : 0,
          tmdb_id: i === currentPartNum ? (movie.tmdb_id || 0) : 0
        });
      }
      // Add upcoming teaser part
      generatedList.push({
        title: `${baseName} ${currentPartNum + 1} (Coming Soon)`,
        year: 2026,
        tmdb_id: 0
      });

      MASTER_FRANCHISES[generatedPackName] = {
        name: generatedPackName,
        alias: [baseName.toLowerCase()],
        poster: movie.poster || '',
        allMovies: generatedList
      };
    }
    return generatedPackName;
  }

  return null;
}