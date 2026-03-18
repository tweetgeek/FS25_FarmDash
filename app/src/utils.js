function _intlLocale(lang) {
  return lang === 'en' ? 'en-US' : 'pl-PL'
}

export function formatMoney(amount, lang = 'pl') {
  return new Intl.NumberFormat(_intlLocale(lang), {
    style: 'currency',
    currency: 'PLN',
    maximumFractionDigits: 0,
  }).format(amount)
}

export function formatPrice(amount, lang = 'pl') {
  return new Intl.NumberFormat(_intlLocale(lang), {
    style: 'decimal',
    maximumFractionDigits: 0,
  }).format(amount) + ' PLN/t'
}

export function round1(n) {
  return Math.round(n * 10) / 10
}
