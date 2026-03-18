import { ref, watch } from 'vue'

/**
 * Returns a ref backed by localStorage.
 * Automatically saves on every change.
 */
export function usePersist(key, defaultValue) {
  const stored = localStorage.getItem(key)
  const initial = stored !== null ? JSON.parse(stored) : defaultValue
  const state = ref(initial)
  watch(state, val => localStorage.setItem(key, JSON.stringify(val)))
  return state
}
