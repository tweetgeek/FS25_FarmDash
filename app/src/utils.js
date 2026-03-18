export function formatMoney(amount) {
  return new Intl.NumberFormat('pl-PL', {
    style: 'currency',
    currency: 'PLN',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function round1(n) {
  return Math.round(n * 10) / 10
}

export function growthModeLabel(mode) {
  const modes = { '1': 'Sezonowy', '2': 'Roczny', '3': 'Wyłączony' }
  return modes[String(mode)] || String(mode || '—')
}

export function fuelLabel(val) {
  const labels = { '1': 'Niska', '2': 'Normalna', '3': 'Wysoka' }
  return labels[String(val)] || String(val || '—')
}
