/*
  app.js
  ======
  Frontend logic for the scoreboard page (index.html). Talks to the
  scoreboard backend (main.py): GET /scoreboard, GET /station-comparison,
  GET /games/{game_id}.
*/

const POLL_INTERVAL_MS = 3000;
let selectedGameId = null;

function formatDuration(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function formatTimestampLabel(isoString) {
  // Short label for the dropdown, e.g. "22.09. 09:00"
  const d = new Date(isoString);
  const pad = n => String(n).padStart(2, '0');
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}. ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// --- Tabs --------------------------------------------------------------

function switchTab(tabId) {
  for (const button of document.querySelectorAll('.tab-button')) {
    const active = button.id === tabId;
    button.setAttribute('aria-selected', String(active));
    document.getElementById(button.getAttribute('aria-controls')).hidden = !active;
  }
}

document.getElementById('tab-ranking').addEventListener('click', () => switchTab('tab-ranking'));
document.getElementById('tab-team').addEventListener('click', () => switchTab('tab-team'));

// --- Ranking tab ---------------------------------------------------------

async function loadScoreboard() {
  const statusEl = document.getElementById('status');
  const tableEl = document.getElementById('ranking-table');
  const bodyEl = document.getElementById('ranking-body');
  const emptyEl = document.getElementById('empty-message');

  try {
    const response = await fetch('/scoreboard');
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    const data = await response.json();

    statusEl.textContent = 'Live';
    statusEl.classList.remove('error');

    updateGameSelect(data.ranking);

    if (data.ranking.length === 0) {
      tableEl.hidden = true;
      emptyEl.hidden = false;
      return;
    }

    emptyEl.hidden = true;
    tableEl.hidden = false;

    bodyEl.innerHTML = data.ranking.map(entry => `
      <tr>
        <td class="rank">${entry.rank}</td>
        <td>${entry.team_name}</td>
        <td class="duration">${formatDuration(entry.duration_seconds)}</td>
      </tr>
    `).join('');

  } catch (err) {
    statusEl.textContent = 'No connection to the server - retrying...';
    statusEl.classList.add('error');
    console.error(err);
  }
}

async function loadStationComparison() {
  const gridEl = document.getElementById('station-grid');

  try {
    const response = await fetch('/station-comparison');
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    const data = await response.json();

    gridEl.innerHTML = data.stations.map(station => `
      <div class="station-card">
        <h3>Station ${station.station_id}</h3>
        <ol>
          ${station.ranking.map(entry => `
            <li>
              <span>${entry.rank}. ${entry.team_name}</span>
              <span class="duration">${formatDuration(entry.duration_seconds)}</span>
            </li>
          `).join('')}
        </ol>
      </div>
    `).join('');

  } catch (err) {
    // The main status line above already shows the connection error -
    // no need for a second one here, just leave the last known state.
    console.error(err);
  }
}

// --- Team detail tab -----------------------------------------------------

function updateGameSelect(ranking) {
  const selectEl = document.getElementById('game-select');
  const previousValue = selectEl.value;

  selectEl.innerHTML = ranking.map(entry =>
    `<option value="${entry.game_id}">${entry.team_name} - ${formatTimestampLabel(entry.started_at)}</option>`
  ).join('');

  if (ranking.length === 0) {
    return;
  }

  // Keep the current selection if it still exists, otherwise pick the first entry.
  const stillExists = ranking.some(entry => String(entry.game_id) === previousValue);
  selectEl.value = stillExists ? previousValue : String(ranking[0].game_id);

  if (selectEl.value !== String(selectedGameId)) {
    selectedGameId = Number(selectEl.value);
    loadGameDetail(selectedGameId);
  }
}

async function loadGameDetail(gameId) {
  const contentEl = document.getElementById('game-detail-content');

  try {
    const response = await fetch(`/games/${gameId}`);
    if (!response.ok) {
      throw new Error(`Server responded with ${response.status}`);
    }
    const detail = await response.json();

    contentEl.innerHTML = `
      <div class="game-overview">
        <div class="team-name">${detail.team_name}</div>
        <div class="overview-stats">
          <div>Total time<strong>${formatDuration(detail.duration_seconds)}</strong></div>
          <div>Overall rank<strong>${detail.overall_rank}</strong></div>
        </div>
      </div>
      <div class="station-grid">
        ${detail.stations.map(s => `
          <div class="station-card">
            <h3>Station ${s.station_id}</h3>
            <ol>
              <li>
                <span>Rank ${s.rank}</span>
                <span class="duration">${formatDuration(s.duration_seconds)}</span>
              </li>
            </ol>
          </div>
        `).join('')}
      </div>
    `;
  } catch (err) {
    contentEl.innerHTML = `<div class="game-detail-placeholder">Could not load this run.</div>`;
    console.error(err);
  }
}

document.getElementById('game-select').addEventListener('change', e => {
  selectedGameId = Number(e.target.value);
  loadGameDetail(selectedGameId);
});

loadScoreboard();
loadStationComparison();
setInterval(loadScoreboard, POLL_INTERVAL_MS);
setInterval(loadStationComparison, POLL_INTERVAL_MS);
