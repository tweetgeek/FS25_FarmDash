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
