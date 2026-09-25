import { STORAGE_KEYS, DEFAULT_MOCK_CODE } from '../constants/index.js'

/**
 * Backend REST API Client for Bomb Defusal Parkour Dashboard Backend
 * Implemented Endpoints:
 * - POST /dashboard/backend/start
 * - POST /dashboard/backend/stop
 * - GET  /dashboard/backend/status
 */
class ApiService {
  constructor() {
    let storedBaseUrl = localStorage.getItem(STORAGE_KEYS.BACKEND_CONFIG)
    // Migrate legacy port 8000 URL if present
    if (storedBaseUrl && (storedBaseUrl.includes(':8000') || storedBaseUrl === 'http://localhost:8000/api')) {
      storedBaseUrl = 'http://localhost:5175'
      localStorage.setItem(STORAGE_KEYS.BACKEND_CONFIG, storedBaseUrl)
    }

    this.baseUrl = storedBaseUrl || 'http://localhost:5175'
    const storedMock = localStorage.getItem(STORAGE_KEYS.MOCK_MODE)
    this.mockMode = storedMock === null ? true : storedMock === 'true'
    this.mockCorrectCode = localStorage.getItem(STORAGE_KEYS.MOCK_CODE) || DEFAULT_MOCK_CODE
    this.mockValidationBehavior = localStorage.getItem(STORAGE_KEYS.MOCK_VALIDATION_BEHAVIOR) || 'normal'
    this.mockCustomMessage = ''
    this.activeGameCode = ''
  }

  setBaseUrl(url) {
    this.baseUrl = (url || '').trim().replace(/\/+$/, '')
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

  getActiveGameCode() {
    return this.activeGameCode
  }

  setActiveGameCode(code) {
    this.activeGameCode = (code || '').trim()
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

  _resolveUrl(path) {
    const trimmedPath = path.startsWith('/') ? path : `/${path}`
    const base = this.baseUrl ? this.baseUrl.trim().replace(/\/+$/, '') : ''

    if (!base) return trimmedPath

    // If base already ends with '/dashboard/backend' and path starts with '/dashboard/backend'
    if (base.endsWith('/dashboard/backend') && trimmedPath.startsWith('/dashboard/backend')) {
      return base + trimmedPath.slice('/dashboard/backend'.length)
    }

    // If base ends with '/api' (legacy), strip it if path starts with '/dashboard/backend'
    if (base.endsWith('/api') && trimmedPath.startsWith('/dashboard/backend')) {
      return base.slice(0, -4) + trimmedPath
    }

    return `${base}${trimmedPath}`
  }

  /**
   * Start a new game
   * POST /dashboard/backend/start
   * @param {{ teamName: string, participantCount: number, durationMs?: number }} payload
   */
  async startGame({ teamName, participantCount, durationMs = 10 * 60 * 1000 }) {
    if (this.mockMode) {
      await this._simulateDelay(400)
      this.activeGameCode = this.mockCorrectCode
      return {
        success: true,
        gameId: 'mock-run-' + Date.now(),
        teamName,
        participantCount,
        startTime: Date.now(),
        durationMs,
        targetEndTime: Date.now() + durationMs,
        code: this.mockCorrectCode,
        message: 'Mock-Spiel erfolgreich gestartet'
      }
    }

    try {
      const url = this._resolveUrl('/dashboard/backend/start')
      const res = await fetch(url, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ 
          team_name: teamName, 
          member_count: Number(participantCount)
        })
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.detail || `Server-Fehler: HTTP ${res.status}`)
      }

      const raw = await res.text()
      let data = {}
      try {
        let parsed = JSON.parse(raw)
        if (typeof parsed === 'string') {
          parsed = JSON.parse(parsed)
        }
        data = parsed && typeof parsed === 'object' ? parsed : { raw: parsed }
      } catch {
        data = { raw }
      }

      const generatedCode = (data && data.code) ? String(data.code).padStart(6, '0') : ''
      if (generatedCode) {
        this.activeGameCode = generatedCode
      }

      return {
        success: true,
        code: generatedCode,
        teamName,
        participantCount,
        startTime: Date.now(),
        durationMs,
        targetEndTime: Date.now() + durationMs,
        ...data
      }
    } catch (err) {
      console.error('API /dashboard/backend/start failed:', err)
      throw err
    }
  }

  /**
   * Stop / abort game
   * POST /dashboard/backend/stop
   * @param {{ outcome?: 'defused' | 'exploded' } | string} [options]
   */
  async stopGame(options = {}) {
    let outcome = 'exploded'
    if (typeof options === 'string') {
      outcome = options
    } else if (options && options.outcome) {
      outcome = options.outcome
    }

    if (this.mockMode) {
      await this._simulateDelay(150)
      return { success: true, outcome, message: 'Mock-Spiel gestoppt' }
    }

    try {
      const url = this._resolveUrl('/dashboard/backend/stop')
      const res = await fetch(url, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ outcome })
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.message || errorData.detail || `Server-Fehler: HTTP ${res.status}`)
      }
      return { success: true, outcome }
    } catch (err) {
      console.warn('API /dashboard/backend/stop warning:', err)
      return { success: false, error: err.message }
    }
  }

  /**
   * Get current station statuses
   * GET /dashboard/backend/status
   * Returns array of station entries: [{ stationDatenId, stationId, spielId, state, rating, timestampStart, timestampEnd }]
   */
  async getGameStatus() {
    if (this.mockMode) {
      return null // managed locally in mock mode
    }

    try {
      const url = this._resolveUrl('/dashboard/backend/status')
      const res = await fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      })
      if (!res.ok) {
        return null
      }
      return await res.json()
    } catch (err) {
      console.warn('API /dashboard/backend/status check warning:', err)
      return null
    }
  }

  /**
   * Validate 6-digit defusal code
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

    // In live mode, validate against backend-generated game code
    const targetCode = this.activeGameCode || this.mockCorrectCode
    const isCorrect = Boolean(targetCode && code === targetCode)

    return {
      success: true,
      correct: isCorrect,
      message: isCorrect 
        ? 'Code korrekt. Bombe entschärft!' 
        : (this.mockCustomMessage || 'Falscher Code. Zugriff verweigert.')
    }
  }

  _simulateDelay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

export const api = new ApiService()
