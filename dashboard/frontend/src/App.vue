<script setup>
import { ref, onMounted } from 'vue'
import { useGameSession } from './composables/useGameSession.js'
import HeaderNav from './components/HeaderNav.vue'
import LandingView from './components/LandingView.vue'
import GameView from './components/GameView.vue'
import ResultView from './components/ResultView.vue'
import SettingsModal from './components/SettingsModal.vue'
import MockingModal from './components/MockingModal.vue'

const { currentView, restoreSession } = useGameSession()
const isSettingsOpen = ref(false)
const isMockUiOpen = ref(false)

onMounted(() => {
  // Check localStorage and restore active game countdown on reload!
  restoreSession()
})
</script>

<template>
  <div class="app-layout">
    <!-- Mission Control Header -->
    <HeaderNav @open-settings="isSettingsOpen = true" />

    <!-- Main View Routing (Pure In-Memory Reactive View, NO URL change!) -->
    <main class="main-content">
      <Transition name="fade-view" mode="out-in">
        <LandingView v-if="currentView === 'landing'" key="landing" />
        <GameView v-else-if="currentView === 'game'" key="game" />
        <ResultView v-else-if="currentView === 'result'" key="result" />
      </Transition>
    </main>

    <!-- Global Settings Modal -->
    <SettingsModal 
      v-if="isSettingsOpen" 
      @close="isSettingsOpen = false" 
      @open-mock-ui="isSettingsOpen = false; isMockUiOpen = true"
    />

    <!-- Dedicated Mocking UI Console -->
    <MockingModal 
      v-if="isMockUiOpen" 
      @close="isMockUiOpen = false"
      @open-settings="isMockUiOpen = false; isSettingsOpen = true"
    />
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
}

/* View transition */
.fade-view-enter-active,
.fade-view-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.fade-view-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.fade-view-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
