<script setup>
import { ref } from 'vue'
import { useGameSession } from '../composables/useGameSession'
import { sounds } from '../services/soundEffects'
import { X, Check, Sliders } from 'lucide-vue-next'

const emit = defineEmits(['close', 'open-mock-ui'])

const { 
  isMockMode, 
  toggleMockMode, 
  backendUrl, 
  updateBackendUrl, 
  mockSolutionCode, 
  updateMockSolutionCode,
  gameDurationMinutes,
  updateGameDuration,
  showHeaderMockBadge,
  toggleShowHeaderMockBadge,
  resetGame
} = useGameSession()

const localBackendUrl = ref(backendUrl.value)
const localMockCode = ref(mockSolutionCode.value)
const localDuration = ref(gameDurationMinutes.value)
const isSaved = ref(false)

const saveSettings = () => {
  updateBackendUrl(localBackendUrl.value)
  updateMockSolutionCode(localMockCode.value)
  updateGameDuration(localDuration.value)
  isSaved.value = true
  sounds.playKeypress()
  setTimeout(() => {
    isSaved.value = false
    emit('close')
  }, 350)
}

const handleResetAll = async () => {
  if (confirm('Laufendes Spiel und alle Daten zurücksetzen?')) {
    await resetGame()
    emit('close')
  }
}
</script>

<template>
  <div class="modal-backdrop" @click.self="emit('close')">
    <div class="modal-card card">
      <!-- Modal Header -->
      <div class="modal-header">
        <h3 class="modal-title">Einstellungen & Mocking</h3>
        <button class="btn-close" @click="emit('close')">
          <X :size="18" />
        </button>
      </div>

      <!-- Modal Body -->
      <div class="modal-body">
        
        <!-- Mock Mode Toggle -->
        <div class="setting-row">
          <div class="setting-text">
            <label class="setting-name">Mock-Modus (Testdaten)</label>
            <p class="setting-hint">Lokale Simulation ohne Verbindung zu externem Backend.</p>
          </div>
          <button 
            type="button" 
            class="switch-control"
            :class="{ 'is-active': isMockMode }"
            @click="toggleMockMode()"
          >
            <span class="switch-thumb"></span>
          </button>
        </div>

        <!-- Mocking UI Launch Card (Only visible when mock mode is on) -->
        <div v-if="isMockMode" class="mock-launch-card">
          <div class="mock-launch-info">
            <div class="mock-launch-title">
              <Sliders :size="16" class="text-blue" />
              <span>Mocking Steuerkonsole</span>
              <span class="pill-badge">Live-Stats</span>
            </div>
            <p class="mock-launch-desc">
              Passe Spielstatus, Stationen 1–6, Countdown, Lösungscodes und Live-Szenarien direkt im Mocking UI an.
            </p>
          </div>
          <button type="button" class="btn btn-primary btn-sm btn-open-mock" @click="emit('open-mock-ui')">
            <Sliders :size="14" />
            <span>Mocking UI öffnen</span>
          </button>
        </div>

        <!-- Backend URL -->
        <div class="setting-col">
          <label class="setting-name">Backend API URL</label>
          <input 
            v-model="localBackendUrl" 
            type="text" 
            placeholder="http://localhost:8000/api"
            :disabled="isMockMode"
            class="setting-input font-mono"
          />
          <span v-if="isMockMode" class="input-note">
            Im Mock-Modus deaktiviert.
          </span>
        </div>

        <!-- Countdown Duration Setting -->
        <div class="setting-col">
          <label class="setting-name">Countdown-Dauer (Minuten)</label>
          <div class="stepper-setting">
            <button 
              type="button" 
              class="btn-step-sm"
              :disabled="localDuration <= 1"
              @click="localDuration = Math.max(1, localDuration - 1)"
            >
              –
            </button>
            <input 
              v-model.number="localDuration" 
              type="number" 
              min="1" 
              max="60" 
              class="setting-input font-mono stepper-input-sm"
            />
            <button 
              type="button" 
              class="btn-step-sm"
              :disabled="localDuration >= 60"
              @click="localDuration = Math.min(60, localDuration + 1)"
            >
              +
            </button>
            <span class="unit-text">Minuten (Standard: 10)</span>
          </div>
          <span class="input-note">
            Startwert für den roten Countdown (Standard: 10 Minuten, anpassbar z.B. zum schnellen Testen).
          </span>
        </div>

        <!-- Mock Solution Code -->
        <div class="setting-col" v-if="isMockMode">
          <label class="setting-name">Mock Entschärfungs-Code (6 Ziffern)</label>
          <input 
            v-model="localMockCode" 
            type="text" 
            maxlength="6"
            placeholder="739215"
            class="setting-input font-mono"
          />
          <span class="input-note">
            Dieser Code gilt im Mock-Modus als korrekte Lösung.
          </span>
        </div>

        <!-- REST API Endpoints Info -->
        <div class="icd-box">
          <span class="icd-title">Backend REST-Endpunkte:</span>
          <div class="icd-items">
            <code>POST /api/game/start</code>
            <code>POST /api/game/stop</code>
            <code>GET  /api/game/status</code>
            <code>POST /api/game/check-code</code>
          </div>
        </div>

      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <button class="btn btn-danger-outline btn-sm" @click="handleResetAll">
          Spiel zurücksetzen
        </button>

        <div class="footer-actions">
          <button class="btn btn-secondary btn-sm" @click="emit('close')">
            Abbrechen
          </button>
          <button class="btn btn-primary btn-sm" @click="saveSettings">
            <Check v-if="isSaved" :size="14" />
            <span>{{ isSaved ? 'Gespeichert' : 'Speichern' }}</span>
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modal-card {
  max-width: 460px;
  width: 100%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-close {
  background: transparent;
  color: var(--text-muted);
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
}

.btn-close:hover {
  color: var(--text-primary);
}

.modal-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.setting-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.setting-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
}

.setting-hint {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.switch-control {
  width: 44px;
  height: 24px;
  background: var(--border-default);
  border-radius: 12px;
  padding: 2px;
  transition: background 0.15s ease;
}

.switch-control.is-active {
  background: var(--red-primary);
}

.switch-thumb {
  display: block;
  width: 20px;
  height: 20px;
  background: #ffffff;
  border-radius: 50%;
  transition: transform 0.15s ease;
  transform: translateX(0);
}

.switch-control.is-active .switch-thumb {
  transform: translateX(20px);
}

.setting-input {
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 0.88rem;
}

.setting-input:focus {
  border-color: var(--border-focus);
}

.setting-input:disabled {
  opacity: 0.5;
}

.stepper-setting {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-step-sm {
  width: 32px;
  height: 32px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-step-sm:hover:not(:disabled) {
  background: var(--bg-subtle);
}

.stepper-input-sm {
  width: 60px;
  text-align: center;
  padding: 6px 8px;
}

.unit-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.input-note {
  font-size: 0.74rem;
  color: var(--text-muted);
}

.icd-box {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  font-size: 0.76rem;
}

.icd-title {
  color: var(--text-muted);
  font-weight: 600;
  display: block;
  margin-bottom: 4px;
}

.icd-items {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.icd-items code {
  font-family: var(--font-mono);
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-top: 1px solid var(--border-subtle);
}

.footer-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 0.82rem;
}

.font-mono {
  font-family: var(--font-mono);
}

.mock-launch-card {
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: var(--radius-md);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.mock-launch-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text-primary);
}

.pill-badge {
  font-size: 0.68rem;
  font-weight: 700;
  background: var(--blue-subtle);
  color: var(--blue-primary);
  padding: 1px 6px;
  border-radius: 4px;
}

.mock-launch-desc {
  font-size: 0.78rem;
  color: var(--text-secondary);
  line-height: 1.35;
  margin-top: 3px;
}

.btn-open-mock {
  width: 100%;
  background: var(--blue-primary);
  border-color: var(--blue-primary);
  gap: 8px;
}

.btn-open-mock:hover {
  background: #2563eb;
  border-color: #2563eb;
}

.text-blue {
  color: var(--blue-primary);
}
</style>
