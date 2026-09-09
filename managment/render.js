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

      const card = document.createElement('div');
      card.className = 'movie-card';
      card.innerHTML = `
        <div class="poster-wrap">
          ${movie.collection ? `<div class="universe-badge">👑 ${escapeHtml(movie.collection)}</div>` : ''}
          ${movie.poster ? `<img src="${movie.poster}" class="poster-img" loading="lazy">` : '<div class="poster-placeholder">No Poster</div>'}
        </div>
        <div class="movie-card-body">
          <div>
            <div class="movie-title">${escapeHtml(movie.title)}</div>
            <div class="movie-meta-row">
              <span>${escapeHtml(movie.year || 'N/A')}</span>
              <span>•</span>
              <span class="spec-chip">${escapeHtml(movie.specs?.resolution || '1080p')}</span>
              ${movie.specs?.size ? `<span class="clean-gb-badge">${escapeHtml(movie.specs.size)}</span>` : ''}
            </div>
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

function handleMovieSearch() { filterAndRenderMovies(); }