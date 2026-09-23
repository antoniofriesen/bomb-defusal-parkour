<script setup>
import { ref } from 'vue'
import { useGameSession } from '../composables/useGameSession'
import { sounds } from '../services/soundEffects'
import { 
  Volume2, 
  VolumeX, 
  ChevronRight
} from 'lucide-vue-next'

const emit = defineEmits(['open-settings'])

const { 
  isGameActive, 
  teamName, 
  formattedMinutes, 
  formattedSeconds, 
  navigateToGame, 
  navigateToLanding 
} = useGameSession()

const isMuted = ref(sounds.isMuted())

const toggleSound = () => {
  isMuted.value = sounds.toggleMute()
  if (!isMuted.value) {
    sounds.playKeypress()
  }
}
</script>

<template>
  <header class="navbar">
    <div class="navbar-inner">
      <!-- Left: Logo & Project Badge (Secret settings trigger) -->
      <div class="brand">
        <div class="brand-title" @click="isGameActive ? navigateToGame() : navigateToLanding()">
          <span>Bomb Defusal</span>
          <span class="brand-sub">Parkour</span>
        </div>
        <button 
          type="button" 
          class="project-pill" 
          @click.stop="emit('open-settings')"
          title="LF07"
        >
          LF07
        </button>
      </div>

      <!-- Center: Active Game Indicator -->
      <div v-if="isGameActive" class="active-indicator" @click="navigateToGame">
        <span class="live-dot"></span>
        <span class="active-label">Spiel aktiv:</span>
        <span class="active-team">{{ teamName || 'Unbenannt' }}</span>
        <span class="active-time">{{ formattedMinutes }}:{{ formattedSeconds }}</span>
        <ChevronRight :size="14" class="text-muted" />
      </div>

      <!-- Right: Controls (clean, only optional sound toggle) -->
      <div class="nav-actions">
        <button 
          class="btn-icon" 
          :title="isMuted ? 'Ton an' : 'Ton aus'"
          @click="toggleSound"
        >
          <VolumeX v-if="isMuted" :size="18" class="text-muted" />
          <Volume2 v-else :size="18" />
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.navbar {
  height: 56px;
  background: var(--bg-app);
  border-bottom: 1px solid var(--border-subtle);
  position: sticky;
  top: 0;
  z-index: 50;
}

.navbar-inner {
  max-width: 1200px;
  height: 100%;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.brand-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
  letter-spacing: -0.01em;
}

.brand-sub {
  color: var(--text-secondary);
  font-weight: 500;
}

.project-pill {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--text-muted);
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
}

.project-pill:hover {
  border-color: var(--border-default);
  color: var(--text-primary);
}

.active-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-surface);
  border: 1px solid var(--red-border);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.82rem;
  cursor: pointer;
  transition: background-color 0.15s ease;
}

.active-indicator:hover {
  background: var(--bg-card);
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--red-primary);
}

.active-label {
  color: var(--text-muted);
}

.active-team {
  font-weight: 600;
  color: var(--text-primary);
}

.active-time {
  font-family: var(--font-mono);
  font-weight: 700;
  color: var(--red-primary);
  margin-left: 2px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-icon {
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
}

.btn-icon:hover {
  background: var(--bg-surface);
  color: var(--text-primary);
  border-color: var(--border-subtle);
}

.text-muted {
  color: var(--text-muted);
}

@media (max-width: 640px) {
  .active-indicator {
    display: none;
  }
}
</style>
