// Web Audio API sound generator for tactical bomb defusal atmosphere
class SoundEffects {
  constructor() {
    this.ctx = null
    this.muted = localStorage.getItem('bomb_defusal_muted') === 'true'
  }

  init() {
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioCtx = window.AudioContext || window.webkitAudioContext
      if (AudioCtx) {
        this.ctx = new AudioCtx()
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume()
    }
  }

  toggleMute() {
    this.muted = !this.muted
    localStorage.setItem('bomb_defusal_muted', String(this.muted))
    return this.muted
  }

  isMuted() {
    return this.muted
  }

  playKeypress() {
    if (this.muted) return
    this.init()
    if (!this.ctx) return

    const osc = this.ctx.createOscillator()
    const gain = this.ctx.createGain()

    osc.type = 'sine'
    osc.frequency.setValueAtTime(800, this.ctx.currentTime)
    osc.frequency.exponentialRampToValueAtTime(1200, this.ctx.currentTime + 0.04)

    gain.gain.setValueAtTime(0.12, this.ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.04)

    osc.connect(gain)
    gain.connect(this.ctx.destination)

    osc.start()
    osc.stop(this.ctx.currentTime + 0.04)
  }

  playTick() {
    if (this.muted) return
    this.init()
    if (!this.ctx) return

    const osc = this.ctx.createOscillator()
    const gain = this.ctx.createGain()

    osc.type = 'triangle'
    osc.frequency.setValueAtTime(1000, this.ctx.currentTime)

    gain.gain.setValueAtTime(0.08, this.ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.03)

    osc.connect(gain)
    gain.connect(this.ctx.destination)

    osc.start()
    osc.stop(this.ctx.currentTime + 0.03)
  }

  playUrgentBeep() {
    if (this.muted) return
    this.init()
    if (!this.ctx) return

    const osc = this.ctx.createOscillator()
    const gain = this.ctx.createGain()

    osc.type = 'sawtooth'
    osc.frequency.setValueAtTime(1500, this.ctx.currentTime)

    gain.gain.setValueAtTime(0.2, this.ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.08)

    osc.connect(gain)
    gain.connect(this.ctx.destination)

    osc.start()
    osc.stop(this.ctx.currentTime + 0.08)
  }

  playSuccess() {
    if (this.muted) return
    this.init()
    if (!this.ctx) return

    const notes = [523.25, 659.25, 783.99, 1046.50] // C5, E5, G5, C6
    notes.forEach((freq, idx) => {
      const osc = this.ctx.createOscillator()
      const gain = this.ctx.createGain()

      osc.type = 'triangle'
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime + idx * 0.1)

      gain.gain.setValueAtTime(0.2, this.ctx.currentTime + idx * 0.1)
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + idx * 0.1 + 0.25)

      osc.connect(gain)
      gain.connect(this.ctx.destination)

      osc.start(this.ctx.currentTime + idx * 0.1)
      osc.stop(this.ctx.currentTime + idx * 0.1 + 0.25)
    })
  }

  playFailure() {
    if (this.muted) return
    this.init()
    if (!this.ctx) return

    const osc = this.ctx.createOscillator()
    const gain = this.ctx.createGain()

    osc.type = 'sawtooth'
    osc.frequency.setValueAtTime(160, this.ctx.currentTime)
    osc.frequency.exponentialRampToValueAtTime(110, this.ctx.currentTime + 0.3)

    gain.gain.setValueAtTime(0.3, this.ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.35)

    osc.connect(gain)
    gain.connect(this.ctx.destination)

    osc.start()
    osc.stop(this.ctx.currentTime + 0.35)
  }

  playAlarm() {
    if (this.muted) return
    this.init()
    if (!this.ctx) return

    for (let i = 0; i < 3; i++) {
      const osc = this.ctx.createOscillator()
      const gain = this.ctx.createGain()

      osc.type = 'sawtooth'
      const start = this.ctx.currentTime + i * 0.25
      osc.frequency.setValueAtTime(800, start)
      osc.frequency.linearRampToValueAtTime(400, start + 0.2)

      gain.gain.setValueAtTime(0.35, start)
      gain.gain.exponentialRampToValueAtTime(0.01, start + 0.2)

      osc.connect(gain)
      gain.connect(this.ctx.destination)

      osc.start(start)
      osc.stop(start + 0.2)
    }
  }
}

export const sounds = new SoundEffects()
