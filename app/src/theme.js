import { ref } from 'vue'

const STORAGE_KEY = 'farmdash_theme'
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'system')

let mql = null

function applyTheme(val) {
  let effective = val
  if (val === 'system') {
    effective = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  document.documentElement.setAttribute('data-theme', effective)
}

function onSystemChange() {
  if (theme.value === 'system') applyTheme('system')
}

function setupSystemListener() {
  if (mql) mql.removeEventListener('change', onSystemChange)
  mql = window.matchMedia('(prefers-color-scheme: dark)')
  if (theme.value === 'system') mql.addEventListener('change', onSystemChange)
}

// Initialize immediately
applyTheme(theme.value)
setupSystemListener()

export function useTheme() {
  function setTheme(val) {
    theme.value = val
    localStorage.setItem(STORAGE_KEY, val)
    applyTheme(val)
    setupSystemListener()
  }
  return { theme, setTheme }
}
