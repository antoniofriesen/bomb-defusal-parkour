<script setup>
import { ref } from 'vue'
import { useGameSession } from '../composables/useGameSession'
import { sounds } from '../services/soundEffects'
import { ArrowRight, AlertCircle } from 'lucide-vue-next'

const { 
  isGameActive, 
  teamName: activeTeamName, 
  participantCount: activePlayerCount,
  formattedMinutes,
  formattedSeconds,
  startGame, 
  isStartingGame, 
  navigateToGame,
  resetGame
} = useGameSession()

const inputTeamName = ref('')
const inputParticipantCount = ref(4)
const errorMessage = ref('')
const showResetConfirm = ref(false)

const handleStartGame = async () => {
  errorMessage.value = ''

  const name = inputTeamName.value.trim()
  if (!name) {
    errorMessage.value = 'Bitte gib einen Teamnamen ein.'
    sounds.playFailure()
    return
  }

  const count = Number(inputParticipantCount.value)
  if (!count || count < 1) {
    errorMessage.value = 'Mindestens 1 Spieler erforderlich.'
    sounds.playFailure()
    return
  }

  try {
    await startGame(name, count)
  } catch (err) {
    errorMessage.value = err.message || 'Fehler beim Starten des Spiels.'
    sounds.playFailure()
  }
}

const confirmResetActiveGame = async () => {
  await resetGame()
  showResetConfirm.value = false
}
</script>

<template>
  <div class="landing-view">
    <div class="landing-container">
      
      <!-- Top Title -->
      <div class="header-block">
        <h1 class="main-title">Neues Spiel starten</h1>
        <p class="main-desc">
          LF07 Parkour-Dashboard: Registriere dein Team. Nach dem Klick auf Start läuft der 10-Minuten-Countdown.
        </p>
      </div>

      <!-- Active Game Banner (if one is currently in progress) -->
      <div v-if="isGameActive" class="active-banner card">
        <div class="banner-content">
          <div class="banner-top">
            <span class="active-badge">Spiel läuft</span>
            <span class="active-timer font-mono">{{ formattedMinutes }}:{{ formattedSeconds }}</span>
          </div>
          <div class="banner-text">
            Aktuell läuft eine Runde für Team <strong>{{ activeTeamName }}</strong> ({{ activePlayerCount }} Spieler). 
            Es kann immer nur ein Spiel zeitgleich stattfinden.
          </div>
          <div class="banner-buttons">
            <button class="btn btn-primary" @click="navigateToGame">
              <span>Zum Countdown</span>
              <ArrowRight :size="16" />
            </button>
            <button class="btn btn-secondary" @click="showResetConfirm = true">
              Spiel abbrechen
            </button>
          </div>
        </div>
      </div>

      <!-- Start Game Form Card -->
      <div class="card form-card">
        <form @submit.prevent="handleStartGame" class="start-form">
          <!-- Team Name -->
          <div class="field-group">
            <label for="team-name" class="field-label">Teamname</label>
            <input 
              id="team-name"
              v-model="inputTeamName"
              type="text" 
              placeholder="z.B. Alpha" 
              maxlength="32"
              :disabled="isGameActive || isStartingGame"
              class="text-input"
              required
            />
          </div>

          <!-- Participant Count -->
          <div class="field-group">
            <label for="participant-count" class="field-label">Anzahl der Spieler</label>
            <div class="stepper-row">
              <button 
                type="button" 
                class="btn-step"
                :disabled="isGameActive || inputParticipantCount <= 1"
                @click="inputParticipantCount = Math.max(1, inputParticipantCount - 1)"
              >
                –
              </button>
              <input 
                id="participant-count"
                v-model.number="inputParticipantCount"
                type="number" 
                min="1" 
                max="12"
                :disabled="isGameActive || isStartingGame"
                class="stepper-input font-mono"
                required
              />
              <button 
                type="button" 
                class="btn-step"
                :disabled="isGameActive || inputParticipantCount >= 12"
                @click="inputParticipantCount = Math.min(12, inputParticipantCount + 1)"
              >
                +
              </button>
            </div>
          </div>

          <!-- Error Alert -->
          <div v-if="errorMessage" class="error-msg">
            <AlertCircle :size="16" />
            <span>{{ errorMessage }}</span>
          </div>

          <!-- Submit Button -->
          <button 
            type="submit" 
            class="btn btn-primary btn-start"
            :disabled="isGameActive || isStartingGame || !inputTeamName.trim()"
          >
            <span>{{ isStartingGame ? 'Wird gestartet...' : 'Spiel starten' }}</span>
          </button>

          <p v-if="isGameActive" class="blocked-note">
            Start gesperrt, da bereits ein aktives Spiel läuft.
          </p>
        </form>
      </div>

      <!-- Compact Process Overview -->
      <div class="process-card card">
        <div class="process-title">Ablauf</div>
        <ol class="process-steps">
          <li><strong>Start:</strong> Die 10 Minuten beginnen sofort zu laufen.</li>
          <li><strong>Stationen:</strong> 6 Stationen liefern jeweils eine Ziffer für den Code.</li>
          <li><strong>Eingabe:</strong> Der 6-stellige Code wird unten geprüft.</li>
        </ol>
      </div>

    </div>

    <!-- Confirm Modal -->
    <div v-if="showResetConfirm" class="modal-backdrop" @click.self="showResetConfirm = false">
      <div class="modal-box card">
        <h3 class="modal-title">Laufendes Spiel beenden?</h3>
        <p class="modal-text">
          Das Spiel von <strong>{{ activeTeamName }}</strong> wird abgebrochen und zurückgesetzt.
        </p>
        <div class="modal-btns">
          <button class="btn btn-secondary" @click="showResetConfirm = false">Abbrechen</button>
          <button class="btn btn-primary" @click="confirmResetActiveGame">Ja, beenden</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.landing-view {
  padding: 48px 20px 80px;
}

.landing-container {
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.header-block {
  text-align: left;
}

.main-title {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.main-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* Active Game Banner */
.active-banner {
  padding: 16px 20px;
  border-color: var(--red-border);
  background: var(--red-subtle);
}

.banner-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.active-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--red-primary);
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid var(--red-border);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}

.active-timer {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--red-primary);
}

.banner-text {
  font-size: 0.86rem;
  color: var(--text-secondary);
  margin-bottom: 14px;
}

.banner-text strong {
  color: var(--text-primary);
}

.banner-buttons {
  display: flex;
  gap: 10px;
}

/* Form Card */
.form-card {
  padding: 24px;
}

.start-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.text-input {
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 10px 14px;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.text-input:focus {
  border-color: var(--border-focus);
}

.text-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stepper-row {
  display: flex;
  align-items: center;
  width: 140px;
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.btn-step {
  width: 40px;
  height: 40px;
  background: var(--bg-card);
  color: var(--text-primary);
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s ease;
}

.btn-step:hover:not(:disabled) {
  background: var(--bg-subtle);
}

.stepper-input {
  width: 60px;
  border: none;
  background: transparent;
  color: var(--text-primary);
  text-align: center;
  font-size: 1rem;
  font-weight: 600;
  -moz-appearance: textfield;
}

.stepper-input::-webkit-outer-spin-button,
.stepper-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--red-subtle);
  border: 1px solid var(--red-border);
  color: #fca5a5;
  font-size: 0.84rem;
  padding: 8px 12px;
  border-radius: var(--radius-sm);
}

.btn-start {
  width: 100%;
  padding: 12px;
  font-size: 0.95rem;
}

.blocked-note {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-align: center;
}

/* Process Card */
.process-card {
  padding: 18px 22px;
}

.process-title {
  font-size: 0.82rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-bottom: 10px;
}

.process-steps {
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.82rem;
  color: var(--text-secondary);
}

.process-steps strong {
  color: var(--text-primary);
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
