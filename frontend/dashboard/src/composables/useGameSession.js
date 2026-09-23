import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { DEFAULT_DURATION_MINUTES, GAME_DURATION_MS, STORAGE_KEYS, INITIAL_STATIONS } from '../constants'
import { api } from '../services/api'
import { sounds } from '../services/soundEffects'
import confetti from 'canvas-confetti'

const storedDuration = typeof window !== 'undefined' ? Number(localStorage.getItem(STORAGE_KEYS.GAME_DURATION)) : null
const gameDurationMinutes = ref(storedDuration && !isNaN(storedDuration) && storedDuration > 0 ? storedDuration : DEFAULT_DURATION_MINUTES)

// Global reactive state to share across components
const currentView = ref('landing') // 'landing' | 'game' | 'result'
const teamName = ref('')
const participantCount = ref(4)
const gameStatus = ref('not_started') // 'not_started' | 'running' | 'defused' | 'detonated' | 'aborted'
const startTime = ref(null)
const targetEndTime = ref(null)
const remainingMs = ref(gameDurationMinutes.value * 60 * 1000)
const isMockMode = ref(api.isMockMode())
const backendUrl = ref(api.getBaseUrl())
const mockSolutionCode = ref(api.getMockCode())
const stations = ref(JSON.parse(JSON.stringify(INITIAL_STATIONS)))
const lastCheckedCode = ref('')
const lastValidationResult = ref(null) // { success: boolean, correct: boolean, message: string }
const isCheckingCode = ref(false)
const isStartingGame = ref(false)
const codeAttempts = ref([])

const isTimerPaused = ref(false)
const mockValidationBehavior = ref(api.getMockValidationBehavior())
const mockCustomErrorMessage = ref(api.getMockCustomMessage())

let timerRafId = null
let timerIntervalId = null
let urgentBeepIntervalId = null

export function useGameSession() {
  // Computed helpers
  const isGameActive = computed(() => {
    return gameStatus.value === 'running' && remainingMs.value > 0
  })

  const formattedMinutes = computed(() => {
    const totalSeconds = Math.max(0, Math.floor(remainingMs.value / 1000))
    const mm = Math.floor(totalSeconds / 60)
    return String(mm).padStart(2, '0')
  })

  const formattedSeconds = computed(() => {
    const totalSeconds = Math.max(0, Math.floor(remainingMs.value / 1000))
    const ss = totalSeconds % 60
    return String(ss).padStart(2, '0')
  })

  const formattedMilliseconds = computed(() => {
    const ms = Math.max(0, remainingMs.value % 1000)
    return String(ms).padStart(3, '0')
  })

  const isUrgent = computed(() => {
    return isGameActive.value && remainingMs.value < 60 * 1000 // under 1 minute!
  })

  const isCritical = computed(() => {
    return isGameActive.value && remainingMs.value < 20 * 1000 // under 20 seconds!
  })

  // Save session state to localStorage
  const persistSession = () => {
    if (typeof window === 'undefined') return

    if (gameStatus.value === 'not_started' || gameStatus.value === 'aborted') {
      localStorage.removeItem(STORAGE_KEYS.GAME_SESSION)
      return
    }

    const sessionData = {
      teamName: teamName.value,
      participantCount: participantCount.value,
      gameStatus: gameStatus.value,
      startTime: startTime.value,
      targetEndTime: targetEndTime.value,
      currentView: currentView.value,
      stations: stations.value,
      codeAttempts: codeAttempts.value,
      lastValidationResult: lastValidationResult.value
    }
    localStorage.setItem(STORAGE_KEYS.GAME_SESSION, JSON.stringify(sessionData))
  }

  // Restore session from localStorage on initial page load
  const restoreSession = () => {
    if (typeof window === 'undefined') return

    const raw = localStorage.getItem(STORAGE_KEYS.GAME_SESSION)
    if (!raw) return

    try {
      const data = JSON.parse(raw)
      teamName.value = data.teamName || ''
      participantCount.value = data.participantCount || 4
      startTime.value = data.startTime || null
      targetEndTime.value = data.targetEndTime || null
      stations.value = data.stations || JSON.parse(JSON.stringify(INITIAL_STATIONS))
      codeAttempts.value = data.codeAttempts || []
      lastValidationResult.value = data.lastValidationResult || null

      if (data.gameStatus === 'running' && data.targetEndTime) {
        const now = Date.now()
        const diff = data.targetEndTime - now

        if (diff > 0) {
          // Game is still running! User must return directly to countdown!
          remainingMs.value = diff
          gameStatus.value = 'running'
          currentView.value = 'game' // URL does not change!
          startTimerLoop()
        } else {
          // Timer expired while page was closed
          remainingMs.value = 0
          gameStatus.value = 'detonated'
          currentView.value = 'result'
        }
      } else if (data.gameStatus === 'defused' || data.gameStatus === 'detonated') {
        gameStatus.value = data.gameStatus
        currentView.value = 'result'
      }
    } catch (e) {
      console.error('Failed to parse saved session:', e)
      localStorage.removeItem(STORAGE_KEYS.GAME_SESSION)
    }
  }

  // Timer loop
  const updateTimer = () => {
    if (!targetEndTime.value || gameStatus.value !== 'running') return

    if (isTimerPaused.value) {
      targetEndTime.value = Date.now() + remainingMs.value
      return
    }

    const now = Date.now()
    const diff = targetEndTime.value - now

    if (diff <= 0) {
      remainingMs.value = 0
      handleDetonation()
    } else {
      remainingMs.value = diff
    }
  }

  let statusPollIntervalId = null

  const startStatusPolling = () => {
    stopStatusPolling()
    if (isMockMode.value) return

    statusPollIntervalId = setInterval(async () => {
      if (gameStatus.value !== 'running' || isMockMode.value) return
      const statusData = await api.getGameStatus()
      if (statusData) {
        if (statusData.stations && Array.isArray(statusData.stations)) {
          stations.value = statusData.stations
        }
        if (statusData.active === false && gameStatus.value === 'running') {
          await resetGame()
        }
      }
    }, 2500)
  }

  const stopStatusPolling = () => {
    if (statusPollIntervalId) {
      clearInterval(statusPollIntervalId)
      statusPollIntervalId = null
    }
  }

  const startTimerLoop = () => {
    stopTimerLoop()

    // 25ms interval provides smooth millisecond rendering with low CPU overhead
    timerIntervalId = setInterval(() => {
      updateTimer()
    }, 25)

    // Poll backend status if live mode
    startStatusPolling()

    // Sound effect trigger for urgency
    urgentBeepIntervalId = setInterval(() => {
      if (isGameActive.value) {
        if (remainingMs.value < 20 * 1000) {
          sounds.playUrgentBeep()
        } else if (remainingMs.value < 60 * 1000 && Math.floor(remainingMs.value / 1000) % 2 === 0) {
          sounds.playUrgentBeep()
        }
      }
    }, 1000)
  }

  const stopTimerLoop = () => {
    stopStatusPolling()
    if (timerIntervalId) {
      clearInterval(timerIntervalId)
      timerIntervalId = null
    }
    if (urgentBeepIntervalId) {
      clearInterval(urgentBeepIntervalId)
      urgentBeepIntervalId = null
    }
    if (timerRafId) {
      cancelAnimationFrame(timerRafId)
      timerRafId = null
    }
  }

  // Start new game action
  const startGame = async (name, count) => {
    if (isGameActive.value) {
      throw new Error('Es läuft bereits ein aktives Spiel! Bitte beende oder setze das aktuelle Spiel zuerst zurück.')
    }

    isStartingGame.value = true
    const totalDurationMs = gameDurationMinutes.value * 60 * 1000
    try {
      const response = await api.startGame({
        teamName: name,
        participantCount: count,
        durationMs: totalDurationMs
      })

      teamName.value = name
      participantCount.value = count
      startTime.value = response.startTime || Date.now()
      targetEndTime.value = response.targetEndTime || (Date.now() + totalDurationMs)
      remainingMs.value = targetEndTime.value - Date.now()
      gameStatus.value = 'running'
      codeAttempts.value = []
      lastValidationResult.value = null

      // Reset station states for fresh run
      resetStations()

      // Switch to game view (countdown) WITHOUT url change!
      currentView.value = 'game'
      startTimerLoop()
      persistSession()
      sounds.playSuccess()

      return response
    } finally {
      isStartingGame.value = false
    }
  }

  // Verify entered defusal code
  const submitCode = async (codeString) => {
    if (!isGameActive.value) {
      throw new Error('Kein aktives Spiel vorhanden!')
    }
    if (!codeString || codeString.length !== 6) {
      throw new Error('Der Code muss genau 6 Ziffern lang sein.')
    }

    isCheckingCode.value = true
    lastCheckedCode.value = codeString

    try {
      const result = await api.checkCode({
        code: codeString,
        teamName: teamName.value
      })

      const attemptRecord = {
        code: codeString,
        timestamp: new Date().toLocaleTimeString(),
        correct: result.correct,
        message: result.message
      }
      codeAttempts.value.unshift(attemptRecord)
      lastValidationResult.value = result

      if (result.correct) {
        // Bomb defused successfully!
        handleDefusal()
      } else {
        sounds.playFailure()
      }

      persistSession()
      return result
    } finally {
      isCheckingCode.value = false
    }
  }

  // Defusal Success
  const handleDefusal = () => {
    stopTimerLoop()
    stopMockStationProgression()
    isTimerPaused.value = false
    gameStatus.value = 'defused'
    if (!lastCheckedCode.value) {
      lastCheckedCode.value = mockSolutionCode.value || '739215'
    }
    currentView.value = 'result'
    persistSession()
    sounds.playSuccess()

    // Trigger victory confetti!
    try {
      confetti({
        particleCount: 150,
        spread: 80,
        origin: { y: 0.6 }
      })
      setTimeout(() => {
        confetti({
          particleCount: 100,
          angle: 60,
          spread: 55,
          origin: { x: 0 }
        })
        confetti({
          particleCount: 100,
          angle: 120,
          spread: 55,
          origin: { x: 1 }
        })
      }, 300)
    } catch (e) {
      console.log('Confetti effect executed', e)
    }
  }

  // Detonation / Time Run Out
  const handleDetonation = () => {
    stopTimerLoop()
    stopMockStationProgression()
    isTimerPaused.value = false
    remainingMs.value = 0
    gameStatus.value = 'detonated'
    currentView.value = 'result'
    persistSession()
    sounds.playAlarm()
  }

  // Abort / Reset game
  const resetGame = async () => {
    stopTimerLoop()
    stopMockStationProgression()
    isTimerPaused.value = false
    await api.stopGame()
    gameStatus.value = 'not_started'
    startTime.value = null
    targetEndTime.value = null
    remainingMs.value = gameDurationMinutes.value * 60 * 1000
    lastValidationResult.value = null
    codeAttempts.value = []
    currentView.value = 'landing'
    resetStations()
    persistSession()
  }

  const resetStations = () => {
    stations.value = INITIAL_STATIONS.map(s => ({
      ...s,
      state: 'idle',
      rating: null,
      timestamp_start: null,
      timestamp_end: null,
      digit: null
    }))
  }

  // Mock station progression helper - removed so stations never change on their own
  const stopMockStationProgression = () => {}

  // Timer Pause / Resume
  const pauseTimer = () => {
    isTimerPaused.value = true
  }

  const resumeTimer = () => {
    isTimerPaused.value = false
    if (gameStatus.value === 'running') {
      targetEndTime.value = Date.now() + remainingMs.value
    }
  }

  const togglePauseTimer = () => {
    if (isTimerPaused.value) {
      resumeTimer()
    } else {
      pauseTimer()
    }
  }

  const setRemainingMs = (ms) => {
    const val = Math.max(0, Number(ms) || 0)
    remainingMs.value = val
    if (gameStatus.value === 'running') {
      targetEndTime.value = Date.now() + val
      if (val === 0) {
        handleDetonation()
        return
      }
    }
    persistSession()
  }

  // Force Game Status & View
  const setGameStatus = (status) => {
    if (status === 'defused') {
      handleDefusal()
      return
    }
    if (status === 'detonated') {
      handleDetonation()
      return
    }
    if (status === 'not_started') {
      stopTimerLoop()
      stopMockStationProgression()
      isTimerPaused.value = false
      gameStatus.value = 'not_started'
      currentView.value = 'landing'
      persistSession()
      return
    }
    if (status === 'running') {
      gameStatus.value = 'running'
      currentView.value = 'game'
      if (!startTime.value) startTime.value = Date.now()
      if (!remainingMs.value || remainingMs.value <= 0) {
        remainingMs.value = gameDurationMinutes.value * 60 * 1000
      }
      targetEndTime.value = Date.now() + remainingMs.value
      startTimerLoop()
      persistSession()
    }
  }

  const setCurrentView = (view) => {
    if (['landing', 'game', 'result'].includes(view)) {
      currentView.value = view
      persistSession()
    }
  }

  // Stations Mock Controls
  const updateStation = (id, updates) => {
    const st = stations.value.find(s => s.id === id)
    if (!st) return
    Object.assign(st, updates)
    persistSession()
  }

  const setAllStations = (state, rating = null) => {
    const code = String(mockSolutionCode.value || '739215').padEnd(6, '0')
    stations.value = stations.value.map((s, idx) => {
      const isSolved = state === 'solved'
      const isActive = state === 'active'
      return {
        ...s,
        state,
        rating: isSolved ? (rating || 'green') : null,
        digit: isSolved ? code[idx] : (s.digit || null),
        timestamp_start: isSolved || isActive ? (s.timestamp_start || new Date().toISOString()) : null,
        timestamp_end: isSolved ? new Date().toISOString() : null
      }
    })
    persistSession()
  }

  const syncStationDigitsWithMockCode = () => {
    const code = String(mockSolutionCode.value || '739215').padEnd(6, '0')
    stations.value.forEach((st, idx) => {
      st.digit = code[idx] || String(idx + 1)
    })
    persistSession()
  }

  const syncMockCodeWithStationDigits = () => {
    const code = stations.value.map(s => s.digit !== null && s.digit !== undefined ? String(s.digit) : '0').join('')
    if (code.length === 6) {
      updateMockSolutionCode(code)
    }
  }

  // Code Attempts Mock Controls
  const addMockAttempt = (code, correct = false, message = null) => {
    const attempt = {
      code: String(code),
      timestamp: new Date().toLocaleTimeString(),
      correct: Boolean(correct),
      message: message || (correct ? 'Code korrekt. Bombe entschärft!' : 'Falscher Code. Zugriff verweigert.')
    }
    codeAttempts.value.unshift(attempt)
    lastCheckedCode.value = String(code)
    lastValidationResult.value = { success: true, correct: attempt.correct, message: attempt.message }
    persistSession()
  }

  const clearCodeAttempts = () => {
    codeAttempts.value = []
    lastValidationResult.value = null
    persistSession()
  }

  // Mock Settings Controls
  const updateMockValidationBehavior = (behavior) => {
    mockValidationBehavior.value = behavior
    api.setMockValidationBehavior(behavior)
  }

  const updateMockCustomErrorMessage = (msg) => {
    mockCustomErrorMessage.value = msg
    api.setMockCustomMessage(msg)
  }

  const updateTeamName = (name) => {
    teamName.value = name
    persistSession()
  }

  const updateParticipantCount = (count) => {
    participantCount.value = Math.max(1, Number(count) || 1)
    persistSession()
  }

  // Presets
  const applyMockPreset = (presetKey) => {
    const code = mockSolutionCode.value || '739215'

    switch (presetKey) {
      case 'fresh':
        stopTimerLoop()
        stopMockStationProgression()
        isTimerPaused.value = false
        teamName.value = 'Team Alpha'
        participantCount.value = 4
        gameStatus.value = 'not_started'
        currentView.value = 'landing'
        remainingMs.value = gameDurationMinutes.value * 60 * 1000
        startTime.value = null
        targetEndTime.value = null
        lastValidationResult.value = null
        codeAttempts.value = []
        resetStations()
        persistSession()
        break

      case 'start':
        stopMockStationProgression()
        isTimerPaused.value = false
        teamName.value = teamName.value || 'Team Alpha'
        participantCount.value = participantCount.value || 4
        gameStatus.value = 'running'
        currentView.value = 'game'
        startTime.value = Date.now()
        remainingMs.value = gameDurationMinutes.value * 60 * 1000
        targetEndTime.value = Date.now() + remainingMs.value
        resetStations()
        codeAttempts.value = []
        lastValidationResult.value = null
        startTimerLoop()
        persistSession()
        break

      case 'midgame':
        stopMockStationProgression()
        isTimerPaused.value = false
        teamName.value = teamName.value || 'Team Alpha'
        participantCount.value = participantCount.value || 4
        gameStatus.value = 'running'
        currentView.value = 'game'
        startTime.value = Date.now() - 5 * 60 * 1000
        remainingMs.value = 5 * 60 * 1000
        targetEndTime.value = Date.now() + remainingMs.value
        stations.value = [
          { id: 1, name: 'Station 1', state: 'solved', rating: 'green', digit: code[0], timestamp_start: new Date(Date.now() - 250000).toISOString(), timestamp_end: new Date(Date.now() - 210000).toISOString() },
          { id: 2, name: 'Station 2', state: 'solved', rating: 'yellow', digit: code[1], timestamp_start: new Date(Date.now() - 200000).toISOString(), timestamp_end: new Date(Date.now() - 150000).toISOString() },
          { id: 3, name: 'Station 3', state: 'solved', rating: 'green', digit: code[2], timestamp_start: new Date(Date.now() - 140000).toISOString(), timestamp_end: new Date(Date.now() - 90000).toISOString() },
          { id: 4, name: 'Station 4', state: 'active', rating: null, digit: null, timestamp_start: new Date(Date.now() - 40000).toISOString(), timestamp_end: null },
          { id: 5, name: 'Station 5', state: 'idle', rating: null, digit: null, timestamp_start: null, timestamp_end: null },
          { id: 6, name: 'Station 6', state: 'idle', rating: null, digit: null, timestamp_start: null, timestamp_end: null },
        ]
        startTimerLoop()
        persistSession()
        break

      case 'critical':
        stopMockStationProgression()
        isTimerPaused.value = false
        teamName.value = teamName.value || 'Team Omega'
        participantCount.value = participantCount.value || 4
        gameStatus.value = 'running'
        currentView.value = 'game'
        startTime.value = Date.now() - 9 * 60 * 1000 - 15 * 1000
        remainingMs.value = 45 * 1000 // 45s remaining!
        targetEndTime.value = Date.now() + remainingMs.value
        stations.value = [
          { id: 1, name: 'Station 1', state: 'solved', rating: 'green', digit: code[0], timestamp_start: new Date(Date.now() - 500000).toISOString(), timestamp_end: new Date(Date.now() - 460000).toISOString() },
          { id: 2, name: 'Station 2', state: 'solved', rating: 'yellow', digit: code[1], timestamp_start: new Date(Date.now() - 450000).toISOString(), timestamp_end: new Date(Date.now() - 390000).toISOString() },
          { id: 3, name: 'Station 3', state: 'solved', rating: 'green', digit: code[2], timestamp_start: new Date(Date.now() - 380000).toISOString(), timestamp_end: new Date(Date.now() - 310000).toISOString() },
          { id: 4, name: 'Station 4', state: 'solved', rating: 'red', digit: code[3], timestamp_start: new Date(Date.now() - 300000).toISOString(), timestamp_end: new Date(Date.now() - 200000).toISOString() },
          { id: 5, name: 'Station 5', state: 'solved', rating: 'green', digit: code[4], timestamp_start: new Date(Date.now() - 190000).toISOString(), timestamp_end: new Date(Date.now() - 110000).toISOString() },
          { id: 6, name: 'Station 6', state: 'solved', rating: 'green', digit: code[5], timestamp_start: new Date(Date.now() - 100000).toISOString(), timestamp_end: new Date(Date.now() - 50000).toISOString() },
        ]
        startTimerLoop()
        persistSession()
        break

      case 'victory':
        stopTimerLoop()
        stopMockStationProgression()
        isTimerPaused.value = false
        teamName.value = teamName.value || 'Team Champion'
        participantCount.value = participantCount.value || 4
        remainingMs.value = 3 * 60 * 1000 + 42 * 1000
        lastCheckedCode.value = code
        stations.value = INITIAL_STATIONS.map((s, i) => ({
          ...s,
          state: 'solved',
          rating: i % 2 === 0 ? 'green' : 'yellow',
          digit: code[i],
          timestamp_start: new Date(Date.now() - 300000).toISOString(),
          timestamp_end: new Date(Date.now() - 240000).toISOString()
        }))
        handleDefusal()
        break

      case 'detonated':
        stopTimerLoop()
        stopMockStationProgression()
        isTimerPaused.value = false
        teamName.value = teamName.value || 'Team Boom'
        participantCount.value = participantCount.value || 4
        stations.value = INITIAL_STATIONS.map((s, i) => ({
          ...s,
          state: i < 3 ? 'solved' : 'active',
          rating: i < 3 ? 'red' : null,
          digit: i < 3 ? code[i] : null,
          timestamp_start: new Date(Date.now() - 300000).toISOString(),
          timestamp_end: i < 3 ? new Date(Date.now() - 240000).toISOString() : null
        }))
        handleDetonation()
        break
    }
  }

  // Toggle Mock Mode
  const toggleMockMode = (val) => {
    const newVal = typeof val === 'boolean' ? val : !isMockMode.value
    isMockMode.value = newVal
    api.setMockMode(newVal)
  }

  const updateBackendUrl = (url) => {
    backendUrl.value = url
    api.setBaseUrl(url)
  }

  const updateMockSolutionCode = (code) => {
    mockSolutionCode.value = code
    api.setMockCode(code)
  }

  const updateGameDuration = (minutes) => {
    const mins = Math.max(1, Math.min(60, Number(minutes) || 10))
    gameDurationMinutes.value = mins
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEYS.GAME_DURATION, String(mins))
    }
    if (gameStatus.value === 'not_started') {
      remainingMs.value = mins * 60 * 1000
    }
  }

  // Return to game view if active
  const navigateToGame = () => {
    if (isGameActive.value) {
      currentView.value = 'game'
    }
  }

  const navigateToLanding = () => {
    currentView.value = 'landing'
  }

  return {
    // State
    currentView,
    teamName,
    participantCount,
    gameStatus,
    remainingMs,
    gameDurationMinutes,
    startTime,
    targetEndTime,
    isMockMode,
    backendUrl,
    mockSolutionCode,
    stations,
    lastCheckedCode,
    lastValidationResult,
    isCheckingCode,
    isStartingGame,
    codeAttempts,
    isTimerPaused,
    mockValidationBehavior,
    mockCustomErrorMessage,

    // Computed
    isGameActive,
    formattedMinutes,
    formattedSeconds,
    formattedMilliseconds,
    isUrgent,
    isCritical,

    // Actions
    restoreSession,
    persistSession,
    startGame,
    submitCode,
    resetGame,
    toggleMockMode,
    updateBackendUrl,
    updateMockSolutionCode,
    updateGameDuration,
    navigateToGame,
    navigateToLanding,

    // Mock Advanced Actions
    pauseTimer,
    resumeTimer,
    togglePauseTimer,
    setRemainingMs,
    setGameStatus,
    setCurrentView,
    updateStation,
    setAllStations,
    syncStationDigitsWithMockCode,
    syncMockCodeWithStationDigits,
    addMockAttempt,
    clearCodeAttempts,
    updateMockValidationBehavior,
    updateMockCustomErrorMessage,
    updateTeamName,
    updateParticipantCount,
    applyMockPreset
  }
}
