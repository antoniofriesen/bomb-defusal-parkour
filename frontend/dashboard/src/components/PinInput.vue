<script setup>
import { ref, watch, nextTick, onMounted } from 'vue'
import { sounds } from '../services/soundEffects'
import { RotateCcw } from 'lucide-vue-next'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  hasError: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'change'])

const digits = ref(['', '', '', '', '', ''])
const inputRefs = ref([])

const setInputRef = (el, idx) => {
  if (el) {
    inputRefs.value[idx] = el
  }
}

const onInput = (event, index) => {
  const value = event.target.value
  sounds.playKeypress()

  if (value.length > 0) {
    const char = value.slice(-1).toUpperCase()
    digits.value[index] = char
    emitChange()

    // Move to next box if available
    if (index < 5 && inputRefs.value[index + 1]) {
      nextTick(() => {
        inputRefs.value[index + 1].focus()
        inputRefs.value[index + 1].select()
      })
    }
  } else {
    digits.value[index] = ''
    emitChange()
  }
}

const onKeyDown = (event, index) => {
  if (event.key === 'Backspace') {
    if (!digits.value[index] && index > 0) {
      digits.value[index - 1] = ''
      emitChange()
      nextTick(() => {
        inputRefs.value[index - 1]?.focus()
      })
    } else {
      digits.value[index] = ''
      emitChange()
    }
  } else if (event.key === 'ArrowLeft' && index > 0) {
    inputRefs.value[index - 1]?.focus()
  } else if (event.key === 'ArrowRight' && index < 5) {
    inputRefs.value[index + 1]?.focus()
  } else if (event.key === 'Enter') {
    event.preventDefault()
    if (getFullCode().length === 6 && !props.disabled) {
      emit('submit', getFullCode())
    }
  }
}

const onPaste = (event) => {
  event.preventDefault()
  const pasted = (event.clipboardData || window.clipboardData).getData('text')
  if (!pasted) return

  const cleaned = pasted.replace(/[^0-9a-zA-Z]/g, '').slice(0, 6).toUpperCase()
  for (let i = 0; i < 6; i++) {
    digits.value[i] = cleaned[i] || ''
  }

  emitChange()
  sounds.playKeypress()

  const nextEmpty = digits.value.findIndex(d => !d)
  const focusIndex = nextEmpty === -1 ? 5 : nextEmpty
  inputRefs.value[focusIndex]?.focus()
}

const getFullCode = () => {
  return digits.value.join('')
}

const emitChange = () => {
  emit('change', getFullCode())
}

const clear = () => {
  digits.value = ['', '', '', '', '', '']
  emitChange()
  inputRefs.value[0]?.focus()
}

defineExpose({
  clear,
  getFullCode,
  focusFirst: () => inputRefs.value[0]?.focus()
})

onMounted(() => {
  inputRefs.value[0]?.focus()
})
</script>

<template>
  <div class="pin-wrapper" :class="{ 'has-error': hasError }">
    <div class="pin-boxes">
      <div 
        v-for="(_, index) in 6" 
        :key="index"
        class="pin-cell"
      >
        <span class="cell-label">Z{{ index + 1 }}</span>
        <input
          :ref="el => setInputRef(el, index)"
          v-model="digits[index]"
          type="text"
          maxlength="1"
          autocomplete="off"
          :disabled="disabled"
          class="pin-input"
          :class="{ 'is-filled': digits[index] !== '' }"
          @input="e => onInput(e, index)"
          @keydown="e => onKeyDown(e, index)"
          @paste="onPaste"
        />
      </div>
    </div>

    <!-- Clear action -->
    <div class="pin-footer">
      <button 
        type="button" 
        class="clear-btn" 
        :disabled="disabled || !digits.some(d => d)" 
        @click="clear"
      >
        <RotateCcw :size="12" />
        <span>Eingabe zurücksetzen</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.pin-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.pin-boxes {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.pin-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.cell-label {
  font-size: 0.7rem;
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--text-muted);
}

.pin-input {
  width: 52px;
  height: 60px;
  background: var(--bg-app);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  font-family: var(--font-mono);
  font-size: 1.8rem;
  font-weight: 700;
  text-align: center;
  caret-color: var(--red-primary);
  transition: border-color 0.15s ease, background-color 0.15s ease;
}

.pin-input:focus {
  border-color: var(--border-focus);
  background: var(--bg-card);
}

.pin-input.is-filled {
  border-color: var(--border-default);
  color: #ffffff;
}

.pin-input:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.has-error .pin-input {
  border-color: var(--red-primary) !important;
  color: #f87171;
}

.pin-footer {
  display: flex;
  justify-content: flex-end;
  width: 100%;
  max-width: 360px;
}

.clear-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.74rem;
  padding: 4px 6px;
  border-radius: var(--radius-sm);
  transition: color 0.15s ease;
}

.clear-btn:hover:not(:disabled) {
  color: var(--text-secondary);
}

.clear-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .pin-boxes {
    gap: 6px;
  }
  .pin-input {
    width: 42px;
    height: 52px;
    font-size: 1.5rem;
  }
}
</style>
