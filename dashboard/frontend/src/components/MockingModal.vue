<script setup>
import { useGameSession } from '../composables/useGameSession.js'
import { sounds } from '../services/soundEffects.js'
import { X, Sliders, Play, Pause, RotateCcw, CheckCircle2, AlertTriangle, Settings, ShieldAlert, Award } from 'lucide-vue-next'

const emit = defineEmits(['close', 'open-settings'])

const {
  stations,
  isTimerPaused,
  togglePauseTimer,
  applyMockPreset,
  updateStation,
  mockSolutionCode,
  updateMockSolutionCode,
  mockValidationBehavior,
  updateMockValidationBehavior,
  mockCustomErrorMessage,
  updateMockCustomErrorMessage,
  resetGame
} = useGameSession()

const presets = [
  { key: 'idle', label: 'Idle / Vorbereitung', desc: 'Stationen zurücksetzen, Timer stoppen' },
  { key: 'start', label: 'Spielstart', desc: 'Frisches Spiel, Countdown läuft' },
  { key: 'midgame', label: 'Halbzeit (3 gelöst)', desc: 'Station 1-3 gelöst, 4 aktiv, 5-6 idle' },
  { key: 'critical', label: 'Kritisch (< 1 Min)', desc: 'Alle Stationen gelöst, Bombe tickt ab!' },
  { key: 'victory', label: 'Entschärfung / Sieg', desc: 'Erfolgreich entschärft, ResultView' },
  { key: 'detonation', label: 'Detonation / Game Over', desc: 'Zeit abgelaufen oder falscher Code' }
]

const handlePreset = (key) => {
  sounds.playKeypress()
  applyMockPreset(key)
}

const toggleStationState = (station) => {
  sounds.playKeypress()
  const states = ['idle', 'active', 'solved']
  const nextIdx = (states.indexOf(station.state) + 1) % states.length
  const nextState = states[nextIdx]
  const digit = nextState === 'solved' ? (mockSolutionCode.value?.[station.id - 1] ?? String(station.id)) : null
  const rating = nextState === 'solved' ? (station.rating || 'green') : null
  updateStation(station.id, {
    state: nextState,
    digit,
    rating,
    timestamp_start: nextState !== 'idle' ? new Date().toISOString() : null,
    timestamp_end: nextState === 'solved' ? new Date().toISOString() : null
  })
}

const cycleRating = (station, e) => {
  e.stopPropagation()
  sounds.playKeypress()
  const ratings = ['green', 'yellow', 'red']
  const nextIdx = (ratings.indexOf(station.rating) + 1) % ratings.length
  updateStation(station.id, { rating: ratings[nextIdx] })
}
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-window">
      <!-- Header -->
      <div class="modal-header">
        <div class="modal-title">
          <Sliders :size="20" class="text-blue" />
          <span>Mocking Steuerkonsole</span>
          <span class="badge-mock">Simulationsmodus</span>
        </div>
        <button class="btn-icon" @click="emit('close')" aria-label="Schließen">
          <X :size="18" />
        </button>
      </div>

      <div class="modal-body">
        <!-- Preset Schnellwahl -->
        <section class="mock-section">
          <h3 class="section-title">Szenarien & Presets</h3>
          <div class="presets-grid">
            <button
              v-for="p in presets"
              :key="p.key"
              class="preset-card"
              @click="handlePreset(p.key)"
            >
              <div class="preset-name">{{ p.label }}</div>
              <div class="preset-desc">{{ p.desc }}</div>
            </button>
          </div>
        </section>

        <!-- Stationen-Status -->
        <section class="mock-section">
          <h3 class="section-title">Stationen (Klicken zum Umschalten: Idle &rarr; Active &rarr; Solved)</h3>
          <div class="stations-mock-grid">
            <div
              v-for="station in stations"
              :key="station.id"
              class="station-mock-item"
              :class="`state-${station.state}`"
              @click="toggleStationState(station)"
            >
              <div class="st-header">
                <strong>Station {{ station.id }}</strong>
                <span class="st-badge">{{ station.state }}</span>
              </div>
              <div class="st-details">
                <span v-if="station.digit !== null" class="st-digit">Ziffer: <b>{{ station.digit }}</b></span>
                <span v-else class="st-digit muted">Keine Ziffer</span>

                <button
                  v-if="station.state === 'solved'"
                  class="rating-badge"
                  :class="station.rating"
                  @click="cycleRating(station, $event)"
                  title="Bewertung wechseln"
                >
                  {{ station.rating || 'green' }}
                </button>
              </div>
            </div>
          </div>
        </section>

        <!-- Timer & Controls -->
        <section class="mock-section">
          <h3 class="section-title">Timer & Spielablauf</h3>
          <div class="action-buttons">
            <button class="btn btn-secondary" @click="togglePauseTimer()">
              <component :is="isTimerPaused ? Play : Pause" :size="16" />
              <span>{{ isTimerPaused ? 'Timer fortsetzen' : 'Timer pausieren' }}</span>
            </button>
            <button class="btn btn-secondary" @click="emit('open-settings')">
              <Settings :size="16" />
              <span>Einstellungen öffnen</span>
            </button>
            <button class="btn btn-danger" @click="resetGame(); emit('close')">
              <RotateCcw :size="16" />
              <span>Spiel zurücksetzen</span>
            </button>
          </div>
        </section>

        <!-- Validierungs-Verhalten -->
        <section class="mock-section">
          <h3 class="section-title">Code-Validierung & Mock-Antwort</h3>
          <div class="validation-row">
            <label class="setting-name">Lösungscode</label>
            <input
              type="text"
              maxlength="6"
              class="setting-input font-mono"
              :value="mockSolutionCode"
              @input="updateMockSolutionCode($event.target.value)"
            />
          </div>
          <div class="validation-row" style="margin-top: 10px;">
            <label class="setting-name">Validierungs-Verhalten</label>
            <select
              class="setting-input"
              :value="mockValidationBehavior"
              @change="updateMockValidationBehavior($event.target.value)"
            >
              <option value="normal">Normal (prüft gegen Lösungscode)</option>
              <option value="always_correct">Immer korrekt (Sieg erzwingen)</option>
              <option value="always_wrong">Immer falsch (Fehler erzwingen)</option>
            </select>
          </div>
        </section>
      </div>

      <!-- Footer -->
      <div class="modal-footer">
        <button class="btn btn-primary" @click="emit('close')">
          Fertig
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-window {
  background: #1e222d;
  color: #e5e7eb;
  border: 1px solid #374151;
  border-radius: 12px;
  width: 100%;
  max-width: 720px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  overflow: hidden;
}

.modal-header {
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #374151;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.15rem;
  font-weight: 600;
}

.text-blue {
  color: #3b82f6;
}

.badge-mock {
  font-size: 0.75rem;
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid #3b82f6;
  border-radius: 9999px;
  padding: 0.15rem 0.6rem;
  margin-left: 0.5rem;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.mock-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9ca3af;
  margin: 0;
}

.presets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.preset-card {
  background: #111827;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 0.75rem;
  text-align: left;
  cursor: pointer;
  transition: all 0.15s ease;
  color: #e5e7eb;
}

.preset-card:hover {
  background: #1f2937;
  border-color: #3b82f6;
  transform: translateY(-1px);
}

.preset-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #93c5fd;
  margin-bottom: 0.25rem;
}

.preset-desc {
  font-size: 0.75rem;
  color: #9ca3af;
}

.stations-mock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 0.75rem;
}

.station-mock-item {
  background: #111827;
  border: 1px solid #374151;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: border-color 0.15s;
}

.station-mock-item:hover {
  border-color: #6b7280;
}

.station-mock-item.state-active {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.08);
}

.station-mock-item.state-solved {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.08);
}

.st-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.st-badge {
  font-size: 0.7rem;
  text-transform: uppercase;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  background: #374151;
}

.state-active .st-badge {
  background: #b45309;
  color: #fef3c7;
}

.state-solved .st-badge {
  background: #065f46;
  color: #d1fae5;
}

.st-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
}

.st-digit.muted {
  color: #6b7280;
}

.rating-badge {
  border: none;
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
  text-transform: capitalize;
  cursor: pointer;
  font-weight: 600;
}

.rating-badge.green {
  background: #10b981;
  color: #064e3b;
}

.rating-badge.yellow {
  background: #f59e0b;
  color: #78350f;
}

.rating-badge.red {
  background: #ef4444;
  color: #7f1d1d;
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.validation-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.setting-name {
  font-size: 0.85rem;
  color: #d1d5db;
}

.setting-input {
  background: #111827;
  border: 1px solid #374151;
  color: #f3f4f6;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
}

.setting-input:focus {
  outline: none;
  border-color: #3b82f6;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: background 0.15s;
}

.btn-primary {
  background: #2563eb;
  color: #ffffff;
}

.btn-primary:hover {
  background: #1d4ed8;
}

.btn-secondary {
  background: #374151;
  color: #f3f4f6;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-danger {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  border: 1px solid #ef4444;
}

.btn-danger:hover {
  background: rgba(239, 68, 68, 0.3);
}

.btn-icon {
  background: transparent;
  border: none;
  color: #9ca3af;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  color: #f3f4f6;
  background: #374151;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #374151;
  display: flex;
  justify-content: flex-end;
}
</style>
