export const DEFAULT_DURATION_MINUTES = 10
export const GAME_DURATION_MS = DEFAULT_DURATION_MINUTES * 60 * 1000 // 10 minutes = 600,000 ms
export const CODE_LENGTH = 6

export const STORAGE_KEYS = {
  GAME_SESSION: 'bomb_defusal_game_session',
  GAME_DURATION: 'bomb_defusal_game_duration',
  MOCK_MODE: 'bomb_defusal_mock_mode',
  MOCK_CODE: 'bomb_defusal_mock_solution',
  BACKEND_CONFIG: 'bomb_defusal_backend_config',
  MUTED: 'bomb_defusal_muted',
  MOCK_AUTO_PROGRESSION: 'bomb_defusal_mock_auto_progression',
  MOCK_VALIDATION_BEHAVIOR: 'bomb_defusal_mock_val_behavior',
  MOCK_HEADER_BADGE: 'bomb_defusal_mock_header_badge'
}

export const INITIAL_STATIONS = [
  { id: 1, name: 'Station 1', state: 'idle', rating: null, timestamp_start: null, timestamp_end: null },
  { id: 2, name: 'Station 2', state: 'idle', rating: null, timestamp_start: null, timestamp_end: null },
  { id: 3, name: 'Station 3', state: 'idle', rating: null, timestamp_start: null, timestamp_end: null },
  { id: 4, name: 'Station 4', state: 'idle', rating: null, timestamp_start: null, timestamp_end: null },
  { id: 5, name: 'Station 5', state: 'idle', rating: null, timestamp_start: null, timestamp_end: null },
  { id: 6, name: 'Station 6', state: 'idle', rating: null, timestamp_start: null, timestamp_end: null },
]

export const DEFAULT_MOCK_CODE = '739215'
