async function apiFetch(url, options) {
  const res = await fetch(url, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Błąd serwera ' + res.status }))
    throw new Error(err.detail || 'Błąd serwera ' + res.status)
  }
  return res.json()
}

export function getConfig() {
  return apiFetch('/api/config')
}

export function getLocalAddress() {
  return apiFetch('/api/local-address')
}

export function saveConfig(data) {
  return apiFetch('/api/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export function detectSavesPath() {
  return apiFetch('/api/detect-saves-path')
}

export function browseFolder() {
  return apiFetch('/api/browse-folder')
}

export function getSaves() {
  return apiFetch('/api/saves')
}

export function getSummary(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/summary`)
}

export function getFields(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/fields`)
}

export function getVehicles(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/vehicles`)
}

export function getWeather(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/weather`)
}

export function getEconomy(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/economy`)
}

export function getStorage(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/storage`)
}

export function getPrecisionFarming(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/precision`)
}

export function getAnimals(saveId) {
  return apiFetch(`/api/save/${encodeURIComponent(saveId)}/animals`)
}
