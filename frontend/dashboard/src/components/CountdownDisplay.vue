<script setup>
import { computed } from 'vue'
import { useGameSession } from '../composables/useGameSession'
import { GAME_DURATION_MS } from '../constants'

const { 
  formattedMinutes, 
  formattedSeconds, 
  formattedMilliseconds, 
  remainingMs, 
  gameDurationMinutes,
  isUrgent, 
  isCritical,
  gameStatus 
} = useGameSession()

const totalDurationMs = computed(() => (gameDurationMinutes.value || 10) * 60 * 1000)

const progressPercentage = computed(() => {
  const pct = (remainingMs.value / totalDurationMs.value) * 100
  return Math.min(100, Math.max(0, pct))
})
</script>

<template>
  <div 
    class="countdown-panel card"
    :class="{
      'panel-urgent': isUrgent,
      'panel-critical': isCritical
    }"
  >
    <!-- Top Header -->
    <div class="panel-header">
      <div class="panel-tag">
        <span class="status-dot" :class="{ 'dot-urgent': isUrgent }"></span>
        <span class="status-label">
          {{ isCritical ? 'KRITISCH – WENIGE SEKUNDEN' : (isUrgent ? 'WARNUNG – UNTER 1 MINUTE' : 'COUNTDOWN LÄUFT') }}
        </span>
      </div>
      <div class="limit-label">
        {{ String(gameDurationMinutes).padStart(2, '0') }}:00:000 Max.
      </div>
    </div>

    <!-- FAT CRISP RED COUNTDOWN -->
    <div class="timer-area">
      <div class="timer-digits">
        <span class="digit-box">{{ formattedMinutes }}</span>
        <span class="separator">:</span>
        <span class="digit-box">{{ formattedSeconds }}</span>
        <span class="separator separator-ms">:</span>
        <span class="digit-box digit-ms">{{ formattedMilliseconds }}</span>
      </div>
    </div>

    <!-- Clean Progress Track -->
    <div class="progress-track">
      <div 
        class="progress-fill" 
        :style="{ width: `${progressPercentage}%` }"
        :class="{ 'fill-urgent': isUrgent }"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.countdown-panel {
  padding: 32px 28px 24px;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  transition: border-color 0.2s ease;
}

.panel-urgent {
  border-color: rgba(239, 68, 68, 0.5);
}

.panel-critical {
  border-color: var(--red-primary);
}

.panel-header {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-tag {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--red-primary);
}

.status-dot.dot-urgent {
  animation: pulse-dot 1s infinite alternate;
}

@keyframes pulse-dot {
  from { opacity: 1; }
  to { opacity: 0.3; }
}

.status-label {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.limit-label {
  font-family: var(--font-mono);
  font-size: 0.74rem;
  color: var(--text-muted);
}

.timer-area {
  padding: 8px 0 20px;
}

.timer-digits {
  display: flex;
  align-items: baseline;
  justify-content: center;
  font-family: var(--font-mono);
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  color: var(--red-primary);
  line-height: 1;
  letter-spacing: -0.04em;
  user-select: none;
}

.digit-box {
  font-size: clamp(3.4rem, 8.5vw, 6.2rem);
}

.digit-ms {
  font-size: clamp(2.4rem, 6.2vw, 4.4rem);
  font-weight: 800;
  color: #f87171;
}

.separator {
  font-size: clamp(2.8rem, 7vw, 5rem);
  color: var(--red-primary);
  opacity: 0.75;
  margin: 0 4px;
}

.separator-ms {
  margin: 0 2px;
}

.progress-track {
  width: 100%;
  height: 4px;
  background: var(--bg-subtle);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 12px;
}

.progress-fill {
  height: 100%;
  background: var(--red-primary);
  transition: width 0.1s linear;
}

.fill-urgent {
  background: #f87171;
}

@media (max-width: 640px) {
  .countdown-panel {
    padding: 20px 16px 16px;
  }
  .separator {
    margin: 0 1px;
  }
}
</style>
