<script setup>
import { computed } from 'vue'
import { useGameSession } from '../composables/useGameSession'
import { GAME_DURATION_MS } from '../constants'
import { CheckCircle2, XCircle, RotateCcw } from 'lucide-vue-next'

const { 
  gameStatus, 
  teamName, 
  participantCount, 
  remainingMs, 
  resetGame, 
  lastCheckedCode
} = useGameSession()

const isVictory = computed(() => gameStatus.value === 'defused')

const timeTakenFormatted = computed(() => {
  const elapsedMs = Math.max(0, GAME_DURATION_MS - remainingMs.value)
  const totalSec = Math.floor(elapsedMs / 1000)
  const mm = String(Math.floor(totalSec / 60)).padStart(2, '0')
  const ss = String(totalSec % 60).padStart(2, '0')
  const ms = String(elapsedMs % 1000).padStart(3, '0')
  return `${mm}:${ss}:${ms}`
})

const timeLeftFormatted = computed(() => {
  const totalSec = Math.floor(remainingMs.value / 1000)
  const mm = String(Math.floor(totalSec / 60)).padStart(2, '0')
  const ss = String(totalSec % 60).padStart(2, '0')
  const ms = String(remainingMs.value % 1000).padStart(3, '0')
  return `${mm}:${ss}:${ms}`
})
</script>

<template>
  <div class="result-view">
    <div class="result-card card" :class="isVictory ? 'is-victory' : 'is-defeat'">
      
      <!-- Icon & Outcome Title -->
      <div class="outcome-header">
        <div class="outcome-icon" :class="isVictory ? 'icon-win' : 'icon-loss'">
          <CheckCircle2 v-if="isVictory" :size="36" />
          <XCircle v-else :size="36" />
        </div>
        <h1 class="outcome-title">
          {{ isVictory ? 'Bombe erfolgreich entschärft' : 'Zeit abgelaufen' }}
        </h1>
        <p class="outcome-desc">
          <span v-if="isVictory">
            Team <strong>{{ teamName }}</strong> hat den korrekten Code rechtzeitig eingegeben.
          </span>
          <span v-else>
            Die vorgegebenen 10 Minuten sind abgelaufen.
          </span>
        </p>
      </div>

      <!-- Stats Grid -->
      <div class="stats-table">
        <div class="stat-row">
          <span class="stat-name">Team</span>
          <span class="stat-value">{{ teamName }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-name">Spieler</span>
          <span class="stat-value">{{ participantCount }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-name">Benötigte Zeit</span>
          <span class="stat-value font-mono">{{ timeTakenFormatted }}</span>
        </div>
        <div class="stat-row">
          <span class="stat-name">Restzeit</span>
          <span class="stat-value font-mono" :class="isVictory ? 'text-green' : 'text-red'">
            {{ timeLeftFormatted }}
          </span>
        </div>
        <div v-if="isVictory" class="stat-row">
          <span class="stat-name">Code</span>
          <span class="stat-value font-mono text-green font-bold">{{ lastCheckedCode }}</span>
        </div>
      </div>

      <!-- Action -->
      <button class="btn btn-primary btn-reset" @click="resetGame">
        <RotateCcw :size="16" />
        <span>Neues Spiel vorbereiten</span>
      </button>

    </div>
  </div>
</template>

<style scoped>
.result-view {
  min-height: calc(100vh - 100px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
}

.result-card {
  max-width: 440px;
  width: 100%;
  padding: 32px 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.is-victory {
  border-color: rgba(16, 185, 129, 0.4);
}

.is-defeat {
  border-color: rgba(239, 68, 68, 0.4);
}

.outcome-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 10px;
}

.outcome-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-win {
  background: var(--green-subtle);
  color: var(--green-primary);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.icon-loss {
  background: var(--red-subtle);
  color: var(--red-primary);
  border: 1px solid var(--red-border);
}

.outcome-title {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

.outcome-desc {
  font-size: 0.88rem;
  color: var(--text-secondary);
}

.outcome-desc strong {
  color: var(--text-primary);
}

.stats-table {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 6px 14px;
  display: flex;
  flex-direction: column;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.86rem;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-name {
  color: var(--text-muted);
}

.stat-value {
  font-weight: 600;
  color: var(--text-primary);
}

.font-mono {
  font-family: var(--font-mono);
}

.font-bold {
  font-weight: 700;
}

.text-green { color: var(--green-primary); }
.text-red { color: var(--red-primary); }

.btn-reset {
  width: 100%;
  padding: 12px;
}
</style>
