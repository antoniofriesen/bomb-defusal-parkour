<script setup>
import { ref } from 'vue'
import { useGameSession } from '../composables/useGameSession'
import CountdownDisplay from './CountdownDisplay.vue'
import PinInput from './PinInput.vue'
import StationsGrid from './StationsGrid.vue'
import { sounds } from '../services/soundEffects'
import { RotateCcw, AlertCircle, CheckCircle2 } from 'lucide-vue-next'

const { 
  teamName, 
  participantCount, 
  submitCode, 
  isCheckingCode, 
  codeAttempts, 
  lastValidationResult,
  resetGame,
  isMockMode,
  mockSolutionCode
} = useGameSession()

const pinInputRef = ref(null)
const currentEnteredCode = ref('')
const hasInputError = ref(false)
const showAbortConfirm = ref(false)

const onCodeChange = (code) => {
  currentEnteredCode.value = code
  hasInputError.value = false
}

const handleCheckCode = async (codeToVerify) => {
  const code = codeToVerify || currentEnteredCode.value
  if (!code || code.length !== 6) {
    hasInputError.value = true
    sounds.playFailure()
    return
  }

  try {
    const result = await submitCode(code)
    if (!result.correct) {
      hasInputError.value = true
    }
  } catch (err) {
    hasInputError.value = true
    console.error('Validation error:', err)
  }
}

const handleFillMockCode = () => {
  const code = mockSolutionCode.value || '739215'
  handleCheckCode(code)
}

const confirmAbort = async () => {
  await resetGame()
  showAbortConfirm.value = false
}
</script>

<template>
  <div class="game-view">
    <div class="game-container">

      <!-- Top Team Meta Bar -->
      <div class="team-bar card">
        <div class="team-info">
          <span class="team-name">{{ teamName || 'Team' }}</span>
          <span class="team-sep">·</span>
          <span class="team-players">{{ participantCount }} Spieler</span>
        </div>
        <button 
          type="button" 
          class="btn-abort" 
          @click="showAbortConfirm = true"
        >
          <RotateCcw :size="13" />
          <span>Spiel abbrechen</span>
        </button>
      </div>

      <!-- FAT RED COUNTDOWN -->
      <CountdownDisplay />

      <!-- CODE DEFUSAL CARD -->
      <div class="code-card card">
        <div class="code-card-header">
          <h2 class="code-title">Entschärfungscode</h2>
          <p class="code-subtitle">Trage die 6 Ziffern der Stationen Z1 bis Z6 ein</p>
        </div>

        <div class="code-body">
          <!-- 6-Pin Input -->
          <PinInput 
            ref="pinInputRef"
            :disabled="isCheckingCode"
            :has-error="hasInputError"
            @change="onCodeChange"
            @submit="handleCheckCode"
          />

          <!-- Check Code Button -->
          <button 
            type="button"
            class="btn btn-primary btn-check"
            :disabled="isCheckingCode || currentEnteredCode.length !== 6"
            @click="() => handleCheckCode(currentEnteredCode)"
          >
            <span v-if="isCheckingCode" class="spinner"></span>
            <span v-else>Code prüfen</span>
          </button>

          <!-- Mock Helper Note (only in mock mode) -->
          <div v-if="isMockMode" class="mock-hint">
            <span>Mock-Testcode: <code>{{ mockSolutionCode }}</code></span>
            <button type="button" class="btn-mock-fill" @click="handleFillMockCode">
              Direkt prüfen
            </button>
          </div>

          <!-- Error Alert -->
          <div 
            v-if="lastValidationResult && !lastValidationResult.correct" 
            class="feedback-error shake"
          >
            <AlertCircle :size="16" />
            <span>{{ lastValidationResult.message || 'Falscher Code!' }}</span>
          </div>
        </div>

        <!-- History of Attempts -->
        <div v-if="codeAttempts.length > 0" class="attempts-section">
          <span class="attempts-label">Bisherige Versuche:</span>
          <div class="attempts-chips">
            <span 
              v-for="(att, i) in codeAttempts.slice(0, 5)" 
              :key="i"
              class="attempt-chip font-mono"
              :class="att.correct ? 'is-correct' : 'is-wrong'"
            >
              {{ att.code }}
              <span class="attempt-icon">{{ att.correct ? '✓' : '✗' }}</span>
            </span>
          </div>
        </div>
      </div>

      <!-- STATIONS MONITOR -->
      <StationsGrid />

    </div>

    <!-- Abort Modal -->
    <div v-if="showAbortConfirm" class="modal-backdrop" @click.self="showAbortConfirm = false">
      <div class="modal-box card">
        <h3 class="modal-title">Spiel wirklich abbrechen?</h3>
        <p class="modal-text">
          Der Countdown wird gestoppt und alle bisherigen Eingaben gehen verloren.
        </p>
        <div class="modal-btns">
          <button class="btn btn-secondary" @click="showAbortConfirm = false">Weiter spielen</button>
          <button class="btn btn-primary" @click="confirmAbort">Ja, abbrechen</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.game-view {
  padding: 32px 20px 80px;
}

.game-container {
  max-width: 820px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Team Bar */
.team-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 18px;
}

.team-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.92rem;
}

.team-name {
  font-weight: 700;
  color: var(--text-primary);
}

.team-sep {
  color: var(--text-muted);
}

.team-players {
  color: var(--text-secondary);
}

.btn-abort {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.78rem;
  padding: 5px 8px;
  border-radius: var(--radius-sm);
  transition: color 0.15s ease;
}

.btn-abort:hover {
  color: #f87171;
}

/* Code Card */
.code-card {
  padding: 24px;
}

.code-card-header {
  text-align: center;
  margin-bottom: 20px;
}

.code-title {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.code-subtitle {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.code-body {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.btn-check {
  width: 100%;
  max-width: 360px;
  padding: 12px;
  font-size: 0.95rem;
}

.mock-hint {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.mock-hint code {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--text-secondary);
}

.btn-mock-fill {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  font-size: 0.74rem;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.btn-mock-fill:hover {
  background: var(--bg-subtle);
  color: var(--text-primary);
}

.feedback-error {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--red-subtle);
  border: 1px solid var(--red-border);
  color: #fca5a5;
  font-size: 0.86rem;
  padding: 10px 16px;
  border-radius: var(--radius-md);
  width: 100%;
  max-width: 360px;
}

/* Attempts */
.attempts-section {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 20px;
  padding-top: 14px;
  border-top: 1px solid var(--border-subtle);
  font-size: 0.76rem;
  color: var(--text-muted);
  flex-wrap: wrap;
}

.attempts-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.attempt-chip {
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--border-subtle);
  background: var(--bg-app);
}

.attempt-chip.is-wrong {
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.3);
}

.attempt-chip.is-correct {
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.3);
}

/* Spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Modal */
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

.modal-box {
  max-width: 400px;
  width: 100%;
  padding: 24px;
}

.modal-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.modal-text {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.modal-btns {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.font-mono {
  font-family: var(--font-mono);
}
</style>
