<script setup>
import { computed } from 'vue'
import { useGameSession } from '../composables/useGameSession'

const { stations } = useGameSession()

const computeDuration = (startStr, endStr) => {
  if (!startStr) return '-'
  const start = new Date(startStr).getTime()
  const end = endStr ? new Date(endStr).getTime() : Date.now()
  const diffSec = Math.max(0, Math.round((end - start) / 1000))
  const mm = String(Math.floor(diffSec / 60)).padStart(2, '0')
  const ss = String(diffSec % 60).padStart(2, '0')
  return `${mm}:${ss}`
}
</script>

<template>
  <div class="stations-card card">
    <div class="card-header">
      <div class="header-left">
        <h3 class="header-title">Stationen (Status)</h3>
        <span class="header-sub">REST-Synchronisation</span>
      </div>
      <div class="badge-solved">
        Gelöst: {{ stations.filter(s => s.state === 'solved').length }} / 6
      </div>
    </div>

    <!-- Stations Grid -->
    <div class="stations-grid">
      <div 
        v-for="st in stations" 
        :key="st.id" 
        class="station-item"
        :class="`is-${st.state}`"
      >
        <div class="station-top">
          <span class="station-name">Station {{ st.id }}</span>
          <span v-if="st.digit !== undefined && st.digit !== null" class="station-digit">
            #{{ st.digit }}
          </span>
        </div>

        <div class="station-details">
          <div class="detail-row">
            <span class="detail-label">Status</span>
            <div class="detail-val">
              <span class="dot state-dot" :class="st.state"></span>
              <span>{{ st.state }}</span>
            </div>
          </div>

          <div class="detail-row">
            <span class="detail-label">Rating</span>
            <div class="detail-val">
              <span v-if="st.rating" class="dot rating-dot" :class="st.rating"></span>
              <span>{{ st.rating || '-' }}</span>
            </div>
          </div>

          <div class="detail-row">
            <span class="detail-label">Dauer</span>
            <span class="font-mono text-muted">{{ computeDuration(st.timestamp_start, st.timestamp_end) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Clean Legend -->
    <div class="card-legend">
      <div class="legend-item">
        <span class="dot state-dot idle"></span>
        <span>idle</span>
      </div>
      <div class="legend-item">
        <span class="dot state-dot active"></span>
        <span>active</span>
      </div>
      <div class="legend-item">
        <span class="dot state-dot solved"></span>
        <span>solved</span>
      </div>
      <span class="legend-divider">|</span>
      <div class="legend-item">
        <span class="dot rating-dot green"></span>
        <span>grün</span>
      </div>
      <div class="legend-item">
        <span class="dot rating-dot yellow"></span>
        <span>gelb</span>
      </div>
      <div class="legend-item">
        <span class="dot rating-dot red"></span>
        <span>rot</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stations-card {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.header-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.header-sub {
  font-size: 0.74rem;
  color: var(--text-muted);
}

.badge-solved {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
}

.stations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.station-item {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: border-color 0.15s ease;
}

.station-item.is-active {
  border-color: rgba(59, 130, 246, 0.4);
}

.station-item.is-solved {
  border-color: rgba(16, 185, 129, 0.4);
}

.station-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.station-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
}

.station-digit {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--blue-primary);
  background: var(--blue-subtle);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 1px 5px;
  border-radius: 4px;
}

.station-details {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.78rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  color: var(--text-muted);
}

.detail-val {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  text-transform: capitalize;
}

.font-mono {
  font-family: var(--font-mono);
}

.text-muted {
  color: var(--text-muted);
}

/* Dots */
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}

.state-dot.idle { background: #52525b; }
.state-dot.active { background: #3b82f6; }
.state-dot.solved { background: #10b981; }

.rating-dot.green { background: #10b981; }
.rating-dot.yellow { background: #eab308; }
.rating-dot.red { background: #ef4444; }

.card-legend {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.74rem;
  color: var(--text-muted);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.legend-divider {
  color: var(--border-default);
}
</style>
