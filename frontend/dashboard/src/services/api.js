import { STORAGE_KEYS, DEFAULT_MOCK_CODE } from '../constants'

/**
 * Backend REST API Client with Mock Mode support
 * Endpoints:
 * - POST /api/game/start
 * - POST /api/game/stop
 * - GET  /api/game/status
 * - POST /api/game/check-code
 */
class ApiService {
  constructor() {
    this.baseUrl = localStorage.getItem(STORAGE_KEYS.BACKEND_CONFIG) || 'http://localhost:8000/api'
    const storedMock = localStorage.getItem(STORAGE_KEYS.MOCK_MODE)
    this.mockMode = storedMock === null ? true : storedMock === 'true'
    this.mockCorrectCode = localStorage.getItem(STORAGE_KEYS.MOCK_CODE) || DEFAULT_MOCK_CODE
    this.mockValidationBehavior = localStorage.getItem(STORAGE_KEYS.MOCK_VALIDATION_BEHAVIOR) || 'normal'
    this.mockCustomMessage = ''
  }

  setBaseUrl(url) {
    this.baseUrl = url.trim().replace(/\/+$/, '')
    localStorage.setItem(STORAGE_KEYS.BACKEND_CONFIG, this.baseUrl)
  }

  getBaseUrl() {
    return this.baseUrl
  }

  isMockMode() {
    return this.mockMode
  }

  setMockMode(enabled) {
    this.mockMode = enabled
    localStorage.setItem(STORAGE_KEYS.MOCK_MODE, String(enabled))
  }

  getMockCode() {
    return this.mockCorrectCode
  }

  setMockCode(code) {
    this.mockCorrectCode = code.trim()
    localStorage.setItem(STORAGE_KEYS.MOCK_CODE, this.mockCorrectCode)
  }

  getMockValidationBehavior() {
    return this.mockValidationBehavior
  }

  setMockValidationBehavior(behavior) {
    this.mockValidationBehavior = behavior
    localStorage.setItem(STORAGE_KEYS.MOCK_VALIDATION_BEHAVIOR, behavior)
  }

  getMockCustomMessage() {
    return this.mockCustomMessage
  }

  setMockCustomMessage(msg) {
    this.mockCustomMessage = msg
  }

  /**
   * Start a new game
   * POST /api/game/start
   * @param {{ teamName: string, participantCount: number, durationMs?: number }} payload
   */
  async startGame({ teamName, participantCount, durationMs = 10 * 60 * 1000 }) {
    if (this.mockMode) {
      await this._simulateDelay(400)
      return {
        success: true,
        gameId: 'mock-run-' + Date.now(),
        teamName,
        participantCount,
        startTime: Date.now(),
        durationMs: durationMs,
        targetEndTime: Date.now() + durationMs,
        message: 'Mock-Spiel erfolgreich gestartet'
      }
    }

    try {
      const res = await fetch(`${this.baseUrl}/game/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          team_name: teamName, 
          participant_count: participantCount,
          duration_seconds: Math.round(durationMs / 1000)
        })
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.detail || `Server-Fehler: HTTP ${res.status}`)
      }
      return await res.json()
    } catch (err) {
      console.error('API /game/start failed:', err)
      throw err
    }
  }

  /**
   * Stop / abort game
   * POST /api/game/stop
   */
  async stopGame() {
    if (this.mockMode) {
      await this._simulateDelay(150)
      return { success: true, message: 'Mock-Spiel gestoppt' }
    }

    try {
      const res = await fetch(`${this.baseUrl}/game/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.detail || `Server-Fehler: HTTP ${res.status}`)
      }
      return await res.json()
    } catch (err) {
      console.warn('API /game/stop warning:', err)
      return { success: false, error: err.message }
    }
  }

  /**
   * Get current game & station status
   * GET /api/game/status
   */
  async getGameStatus() {
    if (this.mockMode) {
      return null // managed locally in mock mode
    }

    try {
      const res = await fetch(`${this.baseUrl}/game/status`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      })
      if (!res.ok) {
        return null
      }
      return await res.json()
    } catch (err) {
      console.warn('API /game/status check warning:', err)
      return null
    }
  }

  /**
   * Validate 6-digit defusal code
   * POST /api/game/check-code
   * @param {{ code: string, teamName?: string }} payload
   */
  async checkCode({ code, teamName }) {
    if (this.mockMode) {
      await this._simulateDelay(450)
      let isCorrect = code === this.mockCorrectCode
      if (this.mockValidationBehavior === 'always_correct') isCorrect = true
      if (this.mockValidationBehavior === 'always_wrong') isCorrect = false

      let message = isCorrect 
        ? 'Code korrekt. Bombe entschärft!' 
        : (this.mockCustomMessage || 'Falscher Code. Zugriff verweigert.')

      return {
        success: true,
        correct: isCorrect,
        message
      }
    }

    try {
      // Primary endpoint POST /game/check-code, fallback to POST /game/check
      let res = await fetch(`${this.baseUrl}/game/check-code`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, team_name: teamName })
      })

      if (res.status === 404) {
        res = await fetch(`${this.baseUrl}/game/check`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, team_name: teamName })
        })
      }

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.detail || `Validierungs-Fehler: HTTP ${res.status}`)
      }
      return await res.json()
    } catch (err) {
      console.error('API checkCode failed:', err)
      throw err
    }
  }

  _simulateDelay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

export const api = new ApiService()
