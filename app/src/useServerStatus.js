import { ref } from 'vue'

export const serverOnline = ref(true)
export const serverRetrying = ref(false)

let retryTimer = null

export function markOffline() {
  if (serverOnline.value) {
    serverOnline.value = false
  }
  if (!retryTimer) {
    retryTimer = setInterval(_retry, 5000)
  }
}

export function markOnline() {
  if (!serverOnline.value) {
    serverOnline.value = true
  }
  if (retryTimer) {
    clearInterval(retryTimer)
    retryTimer = null
  }
  serverRetrying.value = false
}

async function _retry() {
  serverRetrying.value = true
  try {
    const res = await fetch('/api/config', { signal: AbortSignal.timeout(3000) })
    if (res.ok) markOnline()
  } catch {
    // still offline
  } finally {
    serverRetrying.value = false
  }
}
